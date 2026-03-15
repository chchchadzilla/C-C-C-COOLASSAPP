# ═══════════════════════════════════════════════════════════════════════════════
# TASK QUEUE SERVICE — Thread-pool based task runner
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides a bounded thread pool for running agent tasks concurrently.
# Tracks task status, supports cancellation, and integrates with the
# agent_runner service for actual CLI execution.
#
# Usage:
#   from services.task_queue import task_queue
#   task_queue.submit(agent, session, task, repo_path)
#   status = task_queue.get_status(session_id)
#   task_queue.cancel(session_id)
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class TaskInfo:
    session_id: str
    agent_id: str
    task: str
    status: TaskStatus = TaskStatus.QUEUED
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    future: Optional[Future] = None

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'task': self.task[:200],
            'status': self.status.value,
            'submitted_at': self.submitted_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
        }


class TaskQueue:
    """Thread-pool backed task queue with status tracking."""

    def __init__(self, max_workers: int = 10):
        self._max_workers = max_workers
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix='agent-task',
        )
        self._tasks: dict[str, TaskInfo] = {}  # session_id -> TaskInfo
        self._lock = threading.Lock()
        logger.info(f"[TaskQueue] Initialized with max_workers={max_workers}")

    def submit(self, agent, session, task: str, repo_path: str = None,
               model: str = None, timeout: int = 600, app=None) -> TaskInfo:
        """Submit a task for execution in the thread pool."""
        info = TaskInfo(
            session_id=session.session_id,
            agent_id=agent.agent_id,
            task=task,
        )

        with self._lock:
            self._tasks[session.session_id] = info

        def _run_task():
            info.status = TaskStatus.RUNNING
            info.started_at = datetime.now(timezone.utc)

            with app.app_context():
                from services.agent_runner import run_agent_task
                from app import db, socketio
                import json

                socketio.emit('task_status', {
                    'session_id': session.session_id,
                    'status': 'running',
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
                session.outcome_summary = (
                    result['output'][:2000] if result['success']
                    else result['error'][:2000]
                )
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

                db.session.commit()

                # Update task info
                info.status = TaskStatus.COMPLETED if result['success'] else TaskStatus.FAILED
                info.completed_at = datetime.now(timezone.utc)
                info.result = result
                if not result['success']:
                    info.error = result['error'][:500]

                socketio.emit('task_status', {
                    'session_id': session.session_id,
                    'status': info.status.value,
                    'success': result['success'],
                })

                return result

        future = self._executor.submit(_run_task)
        info.future = future
        return info

    def get_status(self, session_id: str) -> Optional[TaskInfo]:
        """Get the status of a task by session ID."""
        with self._lock:
            return self._tasks.get(session_id)

    def cancel(self, session_id: str) -> bool:
        """Cancel a queued or running task."""
        with self._lock:
            info = self._tasks.get(session_id)
        if not info:
            return False

        if info.status == TaskStatus.QUEUED:
            if info.future and info.future.cancel():
                info.status = TaskStatus.CANCELLED
                info.completed_at = datetime.now(timezone.utc)
                return True

        if info.status == TaskStatus.RUNNING:
            from services.agent_runner import cancel_task
            if cancel_task(session_id):
                info.status = TaskStatus.CANCELLED
                info.completed_at = datetime.now(timezone.utc)
                return True

        return False

    def get_all_tasks(self, limit: int = 50) -> list:
        """Return recent tasks (newest first)."""
        with self._lock:
            tasks = sorted(
                self._tasks.values(),
                key=lambda t: t.submitted_at,
                reverse=True,
            )[:limit]
        return [t.to_dict() for t in tasks]

    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        with self._lock:
            tasks = list(self._tasks.values())
        return {
            'total': len(tasks),
            'queued': len([t for t in tasks if t.status == TaskStatus.QUEUED]),
            'running': len([t for t in tasks if t.status == TaskStatus.RUNNING]),
            'completed': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            'failed': len([t for t in tasks if t.status == TaskStatus.FAILED]),
            'cancelled': len([t for t in tasks if t.status == TaskStatus.CANCELLED]),
            'max_workers': self._max_workers,
        }

    def cleanup(self, max_age_hours: int = 24):
        """Remove old completed/failed/cancelled tasks from memory."""
        cutoff = datetime.now(timezone.utc)
        with self._lock:
            to_remove = [
                sid for sid, info in self._tasks.items()
                if info.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
                and info.completed_at
                and (cutoff - info.completed_at).total_seconds() > max_age_hours * 3600
            ]
            for sid in to_remove:
                del self._tasks[sid]
        if to_remove:
            logger.info(f"[TaskQueue] Cleaned up {len(to_remove)} old tasks")


# Global task queue instance
task_queue = TaskQueue(max_workers=10)
