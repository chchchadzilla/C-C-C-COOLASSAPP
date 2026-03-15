# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES — REST API for programmatic access
# ═══════════════════════════════════════════════════════════════════════════════

from functools import wraps
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User, Agent, AgentSession, Report, ImplementationDay, HealthCheck, FailureLog, ProviderConfig
from app import db
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ═══════════════════════════════════════════════════════════════════════════════
# RBAC HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def role_required(*roles):
    """Decorator: restrict endpoint to users with one of the given roles."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions',
                                'required_roles': list(roles)}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator


def _filter_by_ownership(query, model):
    """Apply ownership filtering based on role.
    - admin/orchestrator: see everything
    - developer: see only their own data
    """
    if current_user.role in ('admin', 'orchestrator'):
        return query
    return query.filter(model.user_id == current_user.id)


@api_bp.route('/')
def api_docs():
    """API documentation."""
    return jsonify({
        'name': 'C-C-C-COOLASSAPP API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/users': 'List all users (admin/orchestrator only)',
            'GET /api/agents': 'List agents (scoped by role)',
            'GET /api/agents/<id>/sessions': 'Get agent sessions (scoped by role)',
            'POST /api/agents/<id>/assign': 'Assign task to agent',
            'POST /api/agents/<id>/complete': 'Complete agent task',
            'GET /api/reports': 'List reports',
            'POST /api/reports/generate': 'Generate report (admin/orchestrator)',
            'GET /api/implementation': 'Get implementation plan',
            'GET /api/health': 'Get latest health check',
            'GET /api/failures': 'List failure log',
            'POST /api/failures': 'Log a failure',
            'GET /api/stats': 'Real-time stats',
            'GET /api/providers': 'List configured providers (admin/orchestrator)',
            'POST /api/providers/<id>/test': 'Test a provider connection (admin/orchestrator)',
            'POST /api/chat': 'Send a message through a provider',
            'GET /api/sla': 'SLA stats (mean/median/p95 task duration)',
            'GET /api/queue': 'Task queue status',
        }
    })


@api_bp.route('/users')
@login_required
@role_required('admin', 'orchestrator')
def api_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@api_bp.route('/agents')
@login_required
def api_agents():
    query = _filter_by_ownership(Agent.query, Agent)
    agents = query.all()
    return jsonify([a.to_dict() for a in agents])


@api_bp.route('/agents/<int:agent_id>/sessions')
@login_required
def api_agent_sessions(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    # Developers can only see their own agents' sessions
    if current_user.role not in ('admin', 'orchestrator') and agent.user_id != current_user.id:
        return jsonify({'error': 'Not your agent'}), 403
    sessions = AgentSession.query.filter_by(agent_id=agent_id).order_by(
        AgentSession.started_at.desc()
    ).limit(50).all()
    return jsonify([s.to_dict() for s in sessions])


@api_bp.route('/reports')
@login_required
def api_reports():
    reports = Report.query.order_by(Report.report_date.desc()).limit(30).all()
    return jsonify([r.to_dict() for r in reports])


@api_bp.route('/implementation')
@login_required
def api_implementation():
    days = ImplementationDay.query.order_by(ImplementationDay.day_number).all()
    return jsonify([d.to_dict() for d in days])


@api_bp.route('/health')
@login_required
def api_health():
    check = HealthCheck.query.order_by(HealthCheck.check_date.desc()).first()
    return jsonify(check.to_dict() if check else {})


@api_bp.route('/failures', methods=['GET'])
@login_required
def api_failures():
    failures = FailureLog.query.order_by(FailureLog.timestamp.desc()).all()
    return jsonify([f.to_dict() for f in failures])


@api_bp.route('/stats')
@login_required
def api_stats():
    from sqlalchemy import func
    agents = Agent.query.all()
    
    return jsonify({
        'total_users': User.query.filter_by(is_active=True).count(),
        'total_agents': len(agents),
        'active_agents': len([a for a in agents if a.status == 'active']),
        'idle_agents': len([a for a in agents if a.status == 'idle']),
        'error_agents': len([a for a in agents if a.status == 'error']),
        'total_tasks_completed': sum(a.tasks_completed for a in agents),
        'total_tasks_failed': sum(a.tasks_failed for a in agents),
        'total_merge_conflicts': sum(a.merge_conflicts for a in agents),
        'total_tokens_used': sum(a.tokens_used for a in agents),
        'unresolved_failures': FailureLog.query.filter_by(resolved=False).count()
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER ENDPOINTS — Real provider integration
# ═══════════════════════════════════════════════════════════════════════════════

@api_bp.route('/providers')
@login_required
@role_required('admin', 'orchestrator')
def api_providers():
    """List all configured providers."""
    providers = ProviderConfig.query.order_by(ProviderConfig.priority).all()
    return jsonify([p.to_dict() for p in providers])


@api_bp.route('/providers/<int:provider_id>/test', methods=['POST'])
@login_required
@role_required('admin', 'orchestrator')
def api_test_provider(provider_id):
    """Test a provider connection — real HTTP/CLI call."""
    provider = ProviderConfig.query.get_or_404(provider_id)

    from services.llm_provider import test_provider_connection
    try:
        ok, message = test_provider_connection(provider)
        provider.last_tested_at = datetime.now(timezone.utc)
        provider.last_test_status = 'ok' if ok else 'error'
        provider.last_test_message = message
        db.session.commit()
        return jsonify({'success': ok, 'message': message,
                        'provider': provider.name,
                        'tested_at': provider.last_tested_at.isoformat()})
    except Exception as e:
        provider.last_tested_at = datetime.now(timezone.utc)
        provider.last_test_status = 'error'
        provider.last_test_message = str(e)
        db.session.commit()
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/chat', methods=['POST'])
@login_required
def api_chat():
    """
    Send a message through a configured provider — real LLM call.

    JSON body:
      {
        "provider_id": 1,          // optional — uses default if omitted
        "model": "...",            // optional — uses provider default
        "messages": [              // required
          {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 1024,        // optional
        "temperature": 0.0         // optional
      }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    messages = data.get('messages')
    if not messages or not isinstance(messages, list):
        return jsonify({'error': '"messages" array required'}), 400

    # Resolve provider
    provider_id = data.get('provider_id')
    if provider_id:
        provider = ProviderConfig.query.get(provider_id)
        if not provider:
            return jsonify({'error': f'Provider {provider_id} not found'}), 404
    else:
        from services.llm_provider import get_default_provider
        provider = get_default_provider()
        if not provider:
            return jsonify({'error': 'No enabled provider configured'}), 404

    if not provider.is_enabled:
        return jsonify({'error': f'Provider "{provider.name}" is disabled'}), 400

    from services.llm_provider import send_message
    try:
        result = send_message(
            provider,
            messages=messages,
            model=data.get('model'),
            max_tokens=data.get('max_tokens'),
            temperature=data.get('temperature'),
            user=current_user,
        )
        return jsonify({
            'content': result['content'],
            'model': result['model'],
            'tokens_used': result['tokens_used'],
            'provider': result['provider'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# SLA STATS
# ═══════════════════════════════════════════════════════════════════════════════

@api_bp.route('/sla')
@login_required
def api_sla():
    """SLA stats: mean, median, 95th-percentile task duration."""
    sessions = AgentSession.query.filter(
        AgentSession.status.in_(['completed', 'failed']),
        AgentSession.duration_minutes > 0
    ).all()

    durations = sorted([s.duration_minutes for s in sessions])
    n = len(durations)

    if n == 0:
        return jsonify({
            'count': 0, 'mean': 0, 'median': 0, 'p95': 0,
            'min': 0, 'max': 0,
            'completed': 0, 'failed': 0,
        })

    mean_d = sum(durations) / n
    median_d = durations[n // 2] if n % 2 == 1 else (durations[n // 2 - 1] + durations[n // 2]) / 2
    p95_idx = min(int(n * 0.95), n - 1)
    p95_d = durations[p95_idx]

    completed_count = len([s for s in sessions if s.status == 'completed'])
    failed_count = len([s for s in sessions if s.status == 'failed'])

    return jsonify({
        'count': n,
        'mean': round(mean_d, 2),
        'median': round(median_d, 2),
        'p95': round(p95_d, 2),
        'min': round(durations[0], 2),
        'max': round(durations[-1], 2),
        'completed': completed_count,
        'failed': failed_count,
        'success_rate': round(completed_count / max(completed_count + failed_count, 1) * 100, 1),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# TASK QUEUE
# ═══════════════════════════════════════════════════════════════════════════════

@api_bp.route('/queue')
@login_required
def api_queue():
    """Task queue status and recent tasks."""
    from services.task_queue import task_queue
    return jsonify({
        'stats': task_queue.get_queue_stats(),
        'tasks': task_queue.get_all_tasks(limit=30),
    })


@api_bp.route('/queue/<session_id>')
@login_required
def api_queue_task(session_id):
    """Get status of a specific queued task."""
    from services.task_queue import task_queue
    info = task_queue.get_status(session_id)
    if not info:
        return jsonify({'error': 'Task not found in queue'}), 404
    return jsonify(info.to_dict())
