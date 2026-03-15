# ═══════════════════════════════════════════════════════════════════════════════
# AGENT RUNNER SERVICE — Real CLI execution for Claude Code agents
# ═══════════════════════════════════════════════════════════════════════════════
#
# Wraps the `claude` CLI tool to execute real agent tasks via subprocess.
# Supports:
#   - Synchronous execution (blocking, returns result)
#   - Background execution (threaded, streams output to session log)
#   - Timeout and cancellation
#
# Usage:
#   from services.agent_runner import run_agent_task, run_agent_task_async
#   result = run_agent_task(agent, session, task, repo_path)
#   run_agent_task_async(agent, session, task, repo_path)  # fires in background
#
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import subprocess
import threading
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# In-flight tasks keyed by session_id for cancellation
_running_tasks = {}  # session_id -> subprocess.Popen


def check_claude_cli() -> tuple:
    """Check if the claude CLI is available. Returns (available, version_or_error)."""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, f"CLI returned code {result.returncode}: {result.stderr.strip()}"
    except FileNotFoundError:
        return False, "'claude' not found on PATH"
    except Exception as e:
        return False, str(e)


def run_agent_task(agent, session, task: str, repo_path: str = None,
                   model: str = None, timeout: int = 600,
                   permission_mode: str = None,
                   socketio=None, app=None) -> dict:
    """
    Execute an agent task synchronously via the claude CLI.

    Args:
        agent: Agent model instance
        session: AgentSession model instance
        task: The task/prompt to send to claude
        repo_path: Working directory (repo root) for the CLI
        model: Model override (e.g. 'sonnet', 'opus')
        timeout: Max seconds before killing the process
        permission_mode: Permission mode for claude (default, permissive, etc.)
        socketio: Optional SocketIO instance for live streaming
        app: Optional Flask app for app context (needed when socketio is provided)

    Returns:
        {
            'success': bool,
            'output': str,       # stdout from claude
            'error': str,        # stderr if any
            'exit_code': int,
            'duration_seconds': float,
            'tokens_used': int,  # 0 for CLI (doesn't report tokens)
        }
    """
    model = model or agent.model or 'sonnet'
    cwd = repo_path or os.getcwd()

    cmd = ['claude', '--print']

    # Model selection
    if model:
        cmd += ['--model', model]

    # Permission mode
    pmode = permission_mode or agent.permission_mode
    if pmode and pmode != 'default':
        cmd += ['--dangerously-skip-permissions']

    logger.info(f"[AgentRunner] Starting task for {agent.agent_id}: {task[:100]}...")

    start = datetime.now(timezone.utc)

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )
        _running_tasks[session.session_id] = proc

        # Send task via stdin, then close to signal EOF
        proc.stdin.write(task)
        proc.stdin.close()

        # Stream stdout line-by-line, emitting each via SocketIO for live view
        output_lines = []
        for line in iter(proc.stdout.readline, ''):
            output_lines.append(line)
            if socketio:
                socketio.emit('agent_output', {
                    'session_id': session.session_id,
                    'agent_id': agent.agent_id,
                    'line': line.rstrip('\n'),
                })

        proc.stdout.close()
        stderr = proc.stderr.read()
        proc.stderr.close()

        # Wait for process to finish with timeout
        proc.wait(timeout=timeout)

        stdout = ''.join(output_lines)
        duration = (datetime.now(timezone.utc) - start).total_seconds()

        result = {
            'success': proc.returncode == 0,
            'output': stdout.strip(),
            'error': stderr.strip() if proc.returncode != 0 else '',
            'exit_code': proc.returncode,
            'duration_seconds': round(duration, 2),
            'tokens_used': 0,
        }

        logger.info(
            f"[AgentRunner] Task for {agent.agent_id} finished: "
            f"exit={proc.returncode}, duration={duration:.1f}s"
        )

        return result

    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        logger.warning(f"[AgentRunner] Task for {agent.agent_id} timed out after {timeout}s")
        return {
            'success': False,
            'output': ''.join(output_lines) if 'output_lines' in dir() else '',
            'error': f'Task timed out after {timeout} seconds',
            'exit_code': -1,
            'duration_seconds': round(duration, 2),
            'tokens_used': 0,
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': "'claude' CLI not found — ensure Claude Code is installed and on PATH",
            'exit_code': -1,
            'duration_seconds': 0,
            'tokens_used': 0,
        }
    except Exception as e:
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        logger.exception(f"[AgentRunner] Task for {agent.agent_id} failed")
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'exit_code': -1,
            'duration_seconds': round(duration, 2),
            'tokens_used': 0,
        }
    finally:
        _running_tasks.pop(session.session_id, None)


def run_agent_task_async(agent, session, task: str, repo_path: str = None,
                         model: str = None, timeout: int = 600,
                         app=None):
    """
    Execute an agent task in a background thread.
    Updates the Agent and AgentSession models when complete.
    Emits WebSocket events for live updates.
    """
    def _run():
        # Need app context for DB operations
        with app.app_context():
            from app import db, socketio

            # Emit start event
            socketio.emit('agent_task_started', {
                'agent_id': agent.agent_id,
                'session_id': session.session_id,
                'task': task[:200],
            })

            result = run_agent_task(
                agent, session, task,
                repo_path=repo_path,
                model=model,
                timeout=timeout,
                socketio=socketio,
                app=app,
            )

            # Update session
            session.status = 'completed' if result['success'] else 'failed'
            session.outcome_summary = result['output'][:2000] if result['success'] else result['error'][:2000]
            session.log_output = json.dumps({
                'stdout': result['output'],
                'stderr': result['error'],
                'exit_code': result['exit_code'],
            })
            session.ended_at = datetime.now(timezone.utc)
            session.duration_minutes = result['duration_seconds'] / 60.0
            session.tokens_used = result['tokens_used']

            # Update agent
            if result['success']:
                agent.tasks_completed += 1
            else:
                agent.tasks_failed += 1
            agent.status = 'idle'
            agent.current_task = ''
            agent.last_active = datetime.now(timezone.utc)
            agent.session_count += 1

            # Update user agent count
            from models import User
            user = User.query.get(agent.user_id)
            if user:
                completed_sessions = AgentSession.query.filter_by(
                    agent_id=agent.id
                ).filter(AgentSession.status.in_(['completed', 'failed'])).count()
                # Update avg task duration
                if completed_sessions > 0:
                    from models import AgentSession
                    avg = db.session.query(
                        db.func.avg(AgentSession.duration_minutes)
                    ).filter_by(agent_id=agent.id).filter(
                        AgentSession.status.in_(['completed', 'failed'])
                    ).scalar()
                    agent.avg_task_duration_minutes = round(avg or 0, 2)

            db.session.commit()

            # Emit completion event
            socketio.emit('agent_task_completed', {
                'agent_id': agent.agent_id,
                'session_id': session.session_id,
                'success': result['success'],
                'duration_seconds': result['duration_seconds'],
                'output_preview': result['output'][:500] if result['success'] else result['error'][:500],
            })

    if app is None:
        from flask import current_app
        app = current_app._get_current_object()

    thread = threading.Thread(target=_run, daemon=True, name=f"agent-{agent.agent_id}")
    thread.start()
    return thread


def cancel_task(session_id: str) -> bool:
    """Cancel a running task by session ID."""
    proc = _running_tasks.get(session_id)
    if proc and proc.poll() is None:
        proc.kill()
        logger.info(f"[AgentRunner] Cancelled task for session {session_id}")
        return True
    return False


def get_running_tasks() -> list:
    """Return list of currently running session IDs."""
    return [sid for sid, proc in _running_tasks.items() if proc.poll() is None]
