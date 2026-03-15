# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD ROUTES — Main command center
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import User, Agent, AgentSession, Report, ImplementationDay, HealthCheck, FailureLog
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main orchestration dashboard."""
    # Aggregate stats
    total_users = User.query.filter_by(is_active=True).count()
    total_agents = Agent.query.count()
    active_agents = Agent.query.filter_by(status='active').count()
    
    # Today's stats
    today = datetime.now(timezone.utc).date()
    today_sessions = AgentSession.query.filter(
        func.date(AgentSession.started_at) == today
    ).all()
    
    tasks_today = len(today_sessions)
    completed_today = len([s for s in today_sessions if s.status == 'completed'])
    failed_today = len([s for s in today_sessions if s.status == 'failed'])
    conflicts_today = sum(s.merge_conflicts for s in today_sessions)
    
    # Implementation progress
    impl_days = ImplementationDay.query.order_by(ImplementationDay.day_number).all()
    completed_days = len([d for d in impl_days if d.status == 'completed'])
    current_day = next((d for d in impl_days if d.status == 'in_progress'), None)
    
    # Latest health check
    latest_health = HealthCheck.query.order_by(HealthCheck.check_date.desc()).first()
    
    # Recent failures
    recent_failures = FailureLog.query.filter_by(resolved=False).order_by(
        FailureLog.timestamp.desc()
    ).limit(5).all()
    
    # All users with their agents
    users = User.query.filter_by(is_active=True).all()
    
    return render_template('dashboard/index.html',
                         total_users=total_users,
                         total_agents=total_agents,
                         active_agents=active_agents,
                         tasks_today=tasks_today,
                         completed_today=completed_today,
                         failed_today=failed_today,
                         conflicts_today=conflicts_today,
                         impl_days=impl_days,
                         completed_days=completed_days,
                         current_day=current_day,
                         latest_health=latest_health,
                         recent_failures=recent_failures,
                         users=users)


@dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    """Real-time dashboard stats for WebSocket updates."""
    agents = Agent.query.all()
    return jsonify({
        'agents': [a.to_dict() for a in agents],
        'active_count': len([a for a in agents if a.status == 'active']),
        'idle_count': len([a for a in agents if a.status == 'idle']),
        'error_count': len([a for a in agents if a.status == 'error']),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
