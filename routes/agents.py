# ═══════════════════════════════════════════════════════════════════════════════
# AGENT MANAGEMENT ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

import json
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db, socketio
from models import User, Agent, AgentSession

agents_bp = Blueprint('agents', __name__, url_prefix='/agents')


@agents_bp.route('/')
@login_required
def list_agents():
    """List all agents with real-time status."""
    if current_user.role in ('admin', 'orchestrator'):
        agents = Agent.query.all()
    else:
        agents = Agent.query.filter_by(user_id=current_user.id).all()
    
    users = User.query.filter_by(is_active=True).all()
    return render_template('agents/list.html', agents=agents, users=users)


@agents_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_agent():
    """Create a new Claude Code agent instance."""
    if request.method == 'POST':
        user_id = int(request.form.get('user_id', current_user.id))
        user = User.query.get_or_404(user_id)
        
        # Check agent limit
        current_count = Agent.query.filter_by(user_id=user_id).filter(
            Agent.status != 'terminated'
        ).count()
        
        if current_count >= user.max_agents:
            flash(f'Agent limit reached ({user.max_agents})', 'error')
            return redirect(url_for('agents.list_agents'))
        
        agent = Agent(
            agent_id=f"agent-{uuid.uuid4().hex[:8]}",
            name=request.form.get('name', f'Agent {current_count + 1}'),
            user_id=user_id,
            agent_type=request.form.get('agent_type', 'general'),
            permission_mode=request.form.get('permission_mode', 'default'),
            model=request.form.get('model', 'sonnet')
        )
        db.session.add(agent)
        
        user.current_agent_count = current_count + 1
        db.session.commit()
        
        # Notify via WebSocket
        socketio.emit('agent_created', agent.to_dict())
        
        flash(f'Agent "{agent.name}" created', 'success')
        return redirect(url_for('agents.list_agents'))
    
    users = User.query.filter_by(is_active=True).all()
    return render_template('agents/create.html', users=users)


@agents_bp.route('/<int:agent_id>')
@login_required
def view_agent(agent_id):
    """View agent details and session history."""
    agent = Agent.query.get_or_404(agent_id)
    sessions = AgentSession.query.filter_by(agent_id=agent_id).order_by(
        AgentSession.started_at.desc()
    ).limit(20).all()
    return render_template('agents/detail.html', agent=agent, sessions=sessions)


@agents_bp.route('/<int:agent_id>/assign', methods=['POST'])
@login_required
def assign_task(agent_id):
    """Assign a task to an agent."""
    agent = Agent.query.get_or_404(agent_id)
    
    task = request.form.get('task') or request.json.get('task', '')
    branch = request.form.get('branch') or request.json.get('branch', '')
    files = request.form.get('files') or request.json.get('files', '[]')
    
    agent.current_task = task
    agent.current_branch = branch
    agent.current_files = files if isinstance(files, str) else json.dumps(files)
    agent.status = 'active'
    agent.started_at = datetime.now(timezone.utc)
    
    # Create session record
    session = AgentSession(
        agent_id=agent.id,
        session_id=f"sess-{uuid.uuid4().hex[:8]}",
        task_description=task,
        branch_name=branch
    )
    db.session.add(session)
    db.session.commit()
    
    socketio.emit('agent_updated', agent.to_dict())
    
    if request.is_json:
        return jsonify({'success': True, 'session_id': session.session_id})
    
    flash(f'Task assigned to {agent.name}', 'success')
    return redirect(url_for('agents.view_agent', agent_id=agent_id))


@agents_bp.route('/<int:agent_id>/complete', methods=['POST'])
@login_required
def complete_task(agent_id):
    """Mark an agent's current task as complete."""
    agent = Agent.query.get_or_404(agent_id)
    
    # Accept both form and JSON payloads
    data = request.json if request.is_json else request.form
    
    outcome = data.get('outcome', 'completed')
    summary = data.get('summary', '')
    merge_conflicts = int(data.get('merge_conflicts', 0))
    tests_passed = int(data.get('tests_passed', 0))
    tests_failed = int(data.get('tests_failed', 0))
    tokens = int(data.get('tokens_used', 0))
    files_modified = data.get('files_modified', [])
    if isinstance(files_modified, str):
        try:
            files_modified = json.loads(files_modified)
        except (json.JSONDecodeError, TypeError):
            files_modified = []
    
    # Update agent
    agent.status = 'idle'
    agent.tasks_completed += 1 if outcome == 'completed' else 0
    agent.tasks_failed += 1 if outcome == 'failed' else 0
    agent.merge_conflicts += merge_conflicts
    agent.tokens_used += tokens
    agent.session_count += 1
    agent.last_active = datetime.now(timezone.utc)
    
    # Update session
    session = AgentSession.query.filter_by(
        agent_id=agent.id
    ).order_by(AgentSession.started_at.desc()).first()
    
    if session:
        session.status = outcome
        session.outcome_summary = summary
        session.merge_conflicts = merge_conflicts
        session.tests_passed = tests_passed
        session.tests_failed = tests_failed
        session.tokens_used = tokens
        session.files_modified = json.dumps(files_modified)
        session.ended_at = datetime.now(timezone.utc)
        if session.started_at:
            delta = session.ended_at - session.started_at
            session.duration_minutes = delta.total_seconds() / 60.0
    
    agent.current_task = ''
    agent.current_files = '[]'
    
    db.session.commit()
    socketio.emit('agent_updated', agent.to_dict())
    
    if request.is_json:
        return jsonify({'success': True})
    
    flash(f'Task marked as {outcome}', 'success')
    return redirect(url_for('agents.view_agent', agent_id=agent_id))


@agents_bp.route('/<int:agent_id>/terminate', methods=['POST'])
@login_required
def terminate_agent(agent_id):
    """Terminate an agent."""
    agent = Agent.query.get_or_404(agent_id)
    agent.status = 'terminated'
    
    # Cancel any running task
    from services.agent_runner import cancel_task
    for session in agent.sessions.filter_by(status='running').all():
        cancel_task(session.session_id)
        session.status = 'aborted'
        session.ended_at = datetime.now(timezone.utc)
    
    user = User.query.get(agent.user_id)
    if user:
        # Count AFTER setting status to 'terminated' — query already excludes this agent
        active_count = Agent.query.filter_by(user_id=user.id).filter(
            Agent.status != 'terminated'
        ).count()
        user.current_agent_count = max(active_count, 0)
    
    db.session.commit()
    socketio.emit('agent_terminated', {'agent_id': agent.agent_id})
    
    if request.is_json:
        return jsonify({'success': True})
    
    flash(f'Agent "{agent.name}" terminated', 'warning')
    return redirect(url_for('agents.list_agents'))


@agents_bp.route('/<int:agent_id>/execute', methods=['POST'])
@login_required
def execute_task(agent_id):
    """
    Execute an agent task via the claude CLI — real execution.

    JSON body:
      {
        "task": "Implement the login page",
        "repo_path": "/path/to/repo",      // optional
        "branch": "feature/login",          // optional
        "model": "sonnet",                  // optional
        "timeout": 600,                     // optional, seconds
        "background": true                  // optional, default true
      }
    """
    agent = Agent.query.get_or_404(agent_id)

    if agent.status == 'terminated':
        return jsonify({'error': 'Agent is terminated'}), 400
    if agent.status == 'active':
        return jsonify({'error': 'Agent already has an active task'}), 400

    data = request.get_json(silent=True) or {}
    task = data.get('task', '')
    if not task:
        return jsonify({'error': '"task" is required'}), 400

    repo_path = data.get('repo_path', '')
    branch = data.get('branch', '')
    model = data.get('model', agent.model)
    timeout = int(data.get('timeout', 600))
    background = data.get('background', True)

    # Update agent status
    agent.current_task = task
    agent.current_branch = branch
    agent.status = 'active'
    agent.started_at = datetime.now(timezone.utc)

    # Create session record
    import uuid
    session = AgentSession(
        agent_id=agent.id,
        session_id=f"sess-{uuid.uuid4().hex[:8]}",
        task_description=task,
        branch_name=branch,
    )
    db.session.add(session)
    db.session.commit()

    from services.agent_runner import run_agent_task, run_agent_task_async
    from flask import current_app

    if background:
        run_agent_task_async(
            agent, session, task,
            repo_path=repo_path or None,
            model=model, timeout=timeout,
            app=current_app._get_current_object(),
        )
        return jsonify({
            'success': True,
            'session_id': session.session_id,
            'status': 'running',
            'message': f'Task started in background for {agent.name}',
        })
    else:
        result = run_agent_task(
            agent, session, task,
            repo_path=repo_path or None,
            model=model, timeout=timeout,
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

        # Update agent
        if result['success']:
            agent.tasks_completed += 1
        else:
            agent.tasks_failed += 1
        agent.status = 'idle'
        agent.current_task = ''
        agent.last_active = datetime.now(timezone.utc)
        agent.session_count += 1

        db.session.commit()
        socketio.emit('agent_updated', agent.to_dict())

        return jsonify({
            'success': result['success'],
            'session_id': session.session_id,
            'output': result['output'][:2000],
            'error': result['error'][:500],
            'duration_seconds': result['duration_seconds'],
        })


@agents_bp.route('/<int:agent_id>/sessions/<session_id>/log')
@login_required
def session_log(agent_id, session_id):
    """Get the log output for a specific session."""
    agent = Agent.query.get_or_404(agent_id)
    session = AgentSession.query.filter_by(
        agent_id=agent.id, session_id=session_id
    ).first_or_404()

    log_data = {}
    if session.log_output:
        try:
            log_data = json.loads(session.log_output)
        except (json.JSONDecodeError, TypeError):
            log_data = {'raw': session.log_output}

    if request.is_json or request.args.get('format') == 'json':
        return jsonify({
            'session_id': session.session_id,
            'status': session.status,
            'task': session.task_description,
            'log': log_data,
            'duration_minutes': session.duration_minutes,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
        })

    return render_template('agents/session_log.html',
                           agent=agent, session=session, log_data=log_data)


@agents_bp.route('/cli-status')
@login_required
def cli_status():
    """Check if the claude CLI is available."""
    from services.agent_runner import check_claude_cli, get_running_tasks
    available, version = check_claude_cli()
    running = get_running_tasks()
    return jsonify({
        'cli_available': available,
        'cli_version': version,
        'running_tasks': len(running),
        'running_session_ids': running,
    })


@agents_bp.route('/remote/<int:agent_id>')
@login_required
def remote_view(agent_id):
    """Remote viewing into an agent's current activity."""
    agent = Agent.query.get_or_404(agent_id)
    sessions = AgentSession.query.filter_by(agent_id=agent.id).order_by(
        AgentSession.started_at.desc()
    ).limit(5).all()
    return render_template('agents/remote.html', agent=agent, sessions=sessions)
