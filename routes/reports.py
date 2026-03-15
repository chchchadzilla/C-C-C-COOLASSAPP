# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS ROUTES — Nightly reports and performance analytics
# ═══════════════════════════════════════════════════════════════════════════════

import json
import csv
import io
from flask import Blueprint, render_template, request, jsonify, Response, make_response
from flask_login import login_required
from datetime import datetime, timedelta, timezone, date
from app import db
from models import Report, User, Agent, AgentSession, FailureLog
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def list_reports():
    """List all nightly reports."""
    reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('reports/list.html', reports=reports)


@reports_bp.route('/<int:report_id>')
@login_required
def view_report(report_id):
    """View a specific report."""
    report = Report.query.get_or_404(report_id)
    return render_template('reports/detail.html', report=report)


@reports_bp.route('/generate', methods=['POST'])
@login_required
def generate_report():
    """Manually trigger report generation."""
    from services.report_generator import generate_nightly_report
    report = generate_nightly_report()
    return jsonify({'success': True, 'report_id': report.id})


@reports_bp.route('/analytics')
@login_required
def analytics():
    """Performance analytics dashboard."""
    # Get data for charts
    days = int(request.args.get('days', 14))
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Sessions over time
    sessions = AgentSession.query.filter(
        AgentSession.started_at >= start_date
    ).all()
    
    # Aggregate by date
    daily_stats = {}
    for session in sessions:
        day = session.started_at.date().isoformat()
        if day not in daily_stats:
            daily_stats[day] = {
                'date': day,
                'tasks_completed': 0,
                'tasks_failed': 0,
                'merge_conflicts': 0,
                'tokens_used': 0,
                'total_duration': 0
            }
        if session.status == 'completed':
            daily_stats[day]['tasks_completed'] += 1
        elif session.status == 'failed':
            daily_stats[day]['tasks_failed'] += 1
        daily_stats[day]['merge_conflicts'] += session.merge_conflicts
        daily_stats[day]['tokens_used'] += session.tokens_used
        daily_stats[day]['total_duration'] += session.duration_minutes
    
    # User performance
    users = User.query.filter_by(is_active=True).all()
    user_stats = []
    for user in users:
        agents = Agent.query.filter_by(user_id=user.id).all()
        total_completed = sum(a.tasks_completed for a in agents)
        total_failed = sum(a.tasks_failed for a in agents)
        total_conflicts = sum(a.merge_conflicts for a in agents)
        total_tokens = sum(a.tokens_used for a in agents)
        
        user_stats.append({
            'user': user.to_dict(),
            'tasks_completed': total_completed,
            'tasks_failed': total_failed,
            'merge_conflicts': total_conflicts,
            'tokens_used': total_tokens,
            'success_rate': (total_completed / max(total_completed + total_failed, 1)) * 100,
            'agent_count': len(agents)
        })
    
    # Failure patterns
    failures = FailureLog.query.filter(
        FailureLog.timestamp >= start_date
    ).all()
    
    failure_by_category = {}
    for f in failures:
        cat = f.category
        if cat not in failure_by_category:
            failure_by_category[cat] = {'count': 0, 'resolved': 0, 'unresolved': 0}
        failure_by_category[cat]['count'] += 1
        if f.resolved:
            failure_by_category[cat]['resolved'] += 1
        else:
            failure_by_category[cat]['unresolved'] += 1
    
    return render_template('reports/analytics.html',
                         daily_stats=list(daily_stats.values()),
                         user_stats=user_stats,
                         failure_by_category=failure_by_category,
                         days=days)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT — CSV
# ═══════════════════════════════════════════════════════════════════════════════

@reports_bp.route('/<int:report_id>/export/csv')
@login_required
def export_csv(report_id):
    """Export a report as CSV."""
    report = Report.query.get_or_404(report_id)
    details = json.loads(report.details) if report.details else {}

    buf = io.StringIO()
    writer = csv.writer(buf)

    # Header metadata
    writer.writerow(['Report', f'#{report.id}'])
    writer.writerow(['Date', report.report_date.isoformat() if report.report_date else ''])
    writer.writerow(['Type', report.report_type or ''])
    writer.writerow([])

    # Summary metrics
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Tasks Completed', report.tasks_completed])
    writer.writerow(['Tasks Failed', report.tasks_failed])
    writer.writerow(['Success Rate %', report.success_rate])
    writer.writerow(['Merge Conflicts', report.merge_conflicts])
    writer.writerow(['Total Tokens', report.total_tokens])
    writer.writerow(['Avg Duration (min)', report.avg_duration])
    writer.writerow(['Active Agents', report.active_agents])
    writer.writerow(['Health Score', report.health_score])
    writer.writerow([])

    # Per-user breakdown if available
    user_stats = details.get('user_stats', [])
    if user_stats:
        writer.writerow(['User', 'Completed', 'Failed', 'Conflicts', 'Tokens', 'Agents'])
        for us in user_stats:
            writer.writerow([
                us.get('username', ''),
                us.get('tasks_completed', 0),
                us.get('tasks_failed', 0),
                us.get('merge_conflicts', 0),
                us.get('tokens_used', 0),
                us.get('agent_count', 0),
            ])

    output = buf.getvalue()
    resp = make_response(output)
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename=report_{report.id}.csv'
    return resp


@reports_bp.route('/analytics/export/csv')
@login_required
def export_analytics_csv():
    """Export analytics data as CSV."""
    days = int(request.args.get('days', 14))
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    sessions = AgentSession.query.filter(
        AgentSession.started_at >= start_date
    ).order_by(AgentSession.started_at.desc()).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        'Session ID', 'Agent ID', 'Status', 'Task',
        'Started', 'Duration (min)', 'Tokens', 'Merge Conflicts',
    ])
    for s in sessions:
        writer.writerow([
            s.session_id, s.agent_id, s.status,
            (s.task_description or '')[:120],
            s.started_at.isoformat() if s.started_at else '',
            round(s.duration_minutes, 2) if s.duration_minutes else 0,
            s.tokens_used, s.merge_conflicts,
        ])

    output = buf.getvalue()
    resp = make_response(output)
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename=analytics_{days}d.csv'
    return resp


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT — PDF (simple HTML-to-PDF via basic template rendering)
# ═══════════════════════════════════════════════════════════════════════════════

@reports_bp.route('/<int:report_id>/export/pdf')
@login_required
def export_pdf(report_id):
    """Export a report as a print-friendly HTML page (save as PDF from browser).
    
    NOTE: For true server-side PDF generation, install weasyprint or xhtml2pdf.
    This endpoint returns a minimal styled HTML optimised for File → Print → PDF.
    """
    report = Report.query.get_or_404(report_id)
    details = json.loads(report.details) if report.details else {}

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Report #{report.id}</title>
<style>
  body {{ font-family: 'Inter', Arial, sans-serif; max-width: 800px; margin: 2rem auto; color: #1a1a2e; font-size: 13px; }}
  h1 {{ font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; border-bottom: 2px solid #1a1a2e; padding-bottom: 0.5rem; }}
  h2 {{ font-size: 1.1rem; margin-top: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; }}
  th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; text-align: left; }}
  th {{ background: #f0f0f0; font-weight: 600; }}
  .meta {{ color: #666; font-size: 0.85rem; }}
  @media print {{ body {{ margin: 0; }} }}
</style>
</head><body>
<h1>📊 Report #{report.id} — {report.report_type or 'Nightly'}</h1>
<p class="meta">Generated: {report.report_date.isoformat() if report.report_date else 'N/A'}</p>

<h2>Summary</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Tasks Completed</td><td>{report.tasks_completed}</td></tr>
  <tr><td>Tasks Failed</td><td>{report.tasks_failed}</td></tr>
  <tr><td>Success Rate</td><td>{report.success_rate}%</td></tr>
  <tr><td>Merge Conflicts</td><td>{report.merge_conflicts}</td></tr>
  <tr><td>Total Tokens</td><td>{report.total_tokens:,}</td></tr>
  <tr><td>Avg Duration (min)</td><td>{report.avg_duration}</td></tr>
  <tr><td>Active Agents</td><td>{report.active_agents}</td></tr>
  <tr><td>Health Score</td><td>{report.health_score}</td></tr>
</table>

<p class="meta">Use File → Print → Save as PDF to download.</p>
</body></html>"""

    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp
