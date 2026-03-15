# ═══════════════════════════════════════════════════════════════════════════════
# NIGHTLY REPORT GENERATOR SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

import json
from datetime import datetime, timezone, date
from app import db
from models import Report, User, Agent, AgentSession, FailureLog, HealthCheck
from sqlalchemy import func


def generate_nightly_report(report_date=None):
    """Generate a comprehensive nightly report."""
    if report_date is None:
        report_date = date.today()
    
    # Check if report already exists for this date
    existing = Report.query.filter_by(report_date=report_date).first()
    if existing:
        return existing
    
    # Gather metrics
    users = User.query.filter_by(is_active=True).all()
    agents = Agent.query.all()
    
    # Today's sessions
    sessions = AgentSession.query.filter(
        func.date(AgentSession.started_at) == report_date
    ).all()
    
    total_completed = len([s for s in sessions if s.status == 'completed'])
    total_failed = len([s for s in sessions if s.status == 'failed'])
    total_conflicts = sum(s.merge_conflicts for s in sessions)
    total_tokens = sum(s.tokens_used for s in sessions)
    active_agents = len([a for a in agents if a.status in ('active', 'idle')])
    
    # Success rate
    total_tasks = total_completed + total_failed
    success_rate = (total_completed / max(total_tasks, 1)) * 100
    
    # Per-user breakdown
    user_breakdown = {}
    for user in users:
        user_agents = [a for a in agents if a.user_id == user.id]
        user_sessions = [s for s in sessions if s.agent_id in [a.id for a in user_agents]]
        user_breakdown[user.display_name] = {
            'agents_active': len([a for a in user_agents if a.status in ('active', 'idle')]),
            'tasks_completed': len([s for s in user_sessions if s.status == 'completed']),
            'tasks_failed': len([s for s in user_sessions if s.status == 'failed']),
            'merge_conflicts': sum(s.merge_conflicts for s in user_sessions),
            'tokens_used': sum(s.tokens_used for s in user_sessions)
        }
    
    # Problems solved (completed tasks)
    problems_solved = [
        {'task': s.task_description, 'duration_min': round(s.duration_minutes, 1)}
        for s in sessions if s.status == 'completed' and s.task_description
    ]
    
    # Merge conflict details
    conflict_sessions = [s for s in sessions if s.merge_conflicts > 0]
    conflict_details = [
        {
            'task': s.task_description,
            'conflicts': s.merge_conflicts,
            'branch': s.branch_name,
            'files': json.loads(s.files_modified) if s.files_modified else []
        }
        for s in conflict_sessions
    ]
    
    # Today's failures
    failures = FailureLog.query.filter(
        func.date(FailureLog.timestamp) == report_date
    ).all()
    
    # Latest health check
    health = HealthCheck.query.order_by(HealthCheck.check_date.desc()).first()
    health_score = health.health_score if health else 0.0
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        success_rate, total_conflicts, len(failures), health_score, user_breakdown
    )
    
    # Highlights
    highlights = []
    if total_completed > 0:
        highlights.append(f"✅ {total_completed} tasks completed successfully")
    if total_conflicts == 0:
        highlights.append("🎉 Zero merge conflicts today!")
    if success_rate >= 90:
        highlights.append(f"🏆 {success_rate:.0f}% task success rate")
    
    # Build report HTML
    report_html = _build_report_html(
        report_date, total_completed, total_failed, total_conflicts,
        total_tokens, success_rate, user_breakdown, problems_solved,
        conflict_details, highlights, recommendations, health_score
    )
    
    # Create report record
    report = Report(
        report_date=report_date,
        report_type='nightly',
        total_tasks_completed=total_completed,
        total_tasks_failed=total_failed,
        total_merge_conflicts=total_conflicts,
        total_tokens_used=total_tokens,
        active_agents=active_agents,
        active_users=len(users),
        avg_task_success_rate=success_rate,
        codebase_health_score=health_score,
        user_breakdown=json.dumps(user_breakdown),
        problems_solved=json.dumps(problems_solved),
        merge_conflict_details=json.dumps(conflict_details),
        highlights=json.dumps(highlights),
        recommendations=json.dumps(recommendations),
        report_html=report_html
    )
    
    db.session.add(report)
    db.session.commit()
    
    return report


def _generate_recommendations(success_rate, conflicts, failure_count, health_score, user_breakdown):
    """Generate actionable recommendations based on the day's data."""
    recs = []
    
    if success_rate < 70:
        recs.append({
            'priority': 'high',
            'message': f'Task success rate is {success_rate:.0f}%. Review failing tasks for common patterns. Consider reducing agent count per person and improving task scoping.'
        })
    
    if conflicts > 5:
        recs.append({
            'priority': 'high',
            'message': f'{conflicts} merge conflicts today. Review file ownership boundaries. Ensure agents are working on non-overlapping files.'
        })
    
    if failure_count > 3:
        recs.append({
            'priority': 'medium',
            'message': f'{failure_count} failures logged today. Check the failure log for patterns. Common causes: context drift, stale branches, conflicting CLAUDE.md instructions.'
        })
    
    if health_score < 60:
        recs.append({
            'priority': 'high',
            'message': f'Codebase health score is {health_score:.0f}/100. Run a full health check and address lint errors, failing tests, or stale branches.'
        })
    
    # Check for user struggling
    for user_name, stats in user_breakdown.items():
        user_total = stats['tasks_completed'] + stats['tasks_failed']
        if user_total > 0:
            user_success = (stats['tasks_completed'] / user_total) * 100
            if user_success < 50:
                recs.append({
                    'priority': 'medium',
                    'message': f'{user_name} has a {user_success:.0f}% success rate. Consider pairing them with a more experienced orchestrator or reducing their agent count.'
                })
    
    if not recs:
        recs.append({
            'priority': 'low',
            'message': '✨ Great day! All metrics within healthy ranges. Consider pushing agent counts up if team is comfortable.'
        })
    
    return recs


def _build_report_html(report_date, completed, failed, conflicts, tokens,
                       success_rate, user_breakdown, problems_solved,
                       conflict_details, highlights, recommendations, health_score):
    """Build a formatted HTML report."""
    return f"""
    <div class="nightly-report">
        <h2>📊 Nightly Orchestration Report — {report_date}</h2>
        
        <div class="report-summary">
            <div class="metric">
                <span class="metric-value">{completed}</span>
                <span class="metric-label">Tasks Completed</span>
            </div>
            <div class="metric">
                <span class="metric-value">{failed}</span>
                <span class="metric-label">Tasks Failed</span>
            </div>
            <div class="metric">
                <span class="metric-value">{conflicts}</span>
                <span class="metric-label">Merge Conflicts</span>
            </div>
            <div class="metric">
                <span class="metric-value">{success_rate:.0f}%</span>
                <span class="metric-label">Success Rate</span>
            </div>
            <div class="metric">
                <span class="metric-value">{health_score:.0f}</span>
                <span class="metric-label">Health Score</span>
            </div>
        </div>
        
        <h3>🌟 Highlights</h3>
        <ul>{''.join(f'<li>{h}</li>' for h in highlights)}</ul>
        
        <h3>📋 Recommendations</h3>
        <ul>{''.join(f'<li class="priority-{r["priority"]}">{r["message"]}</li>' for r in recommendations)}</ul>
    </div>
    """
