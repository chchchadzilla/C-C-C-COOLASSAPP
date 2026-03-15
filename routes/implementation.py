# ═══════════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION TRACKER ROUTES — 2-week plan management
# ═══════════════════════════════════════════════════════════════════════════════

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime, timezone
from app import db
from models import ImplementationDay, FailureLog

implementation_bp = Blueprint('implementation', __name__, url_prefix='/implementation')


@implementation_bp.route('/')
@login_required
def plan_overview():
    """View the full 2-week implementation plan."""
    days = ImplementationDay.query.order_by(ImplementationDay.day_number).all()
    
    # Calculate progress
    total = len(days)
    completed = len([d for d in days if d.status == 'completed'])
    in_progress = len([d for d in days if d.status == 'in_progress'])
    blocked = len([d for d in days if d.status == 'blocked'])
    
    # Get failure log entries per day
    failures = FailureLog.query.all()
    failures_by_day = {}
    for f in failures:
        if f.implementation_day:
            if f.implementation_day not in failures_by_day:
                failures_by_day[f.implementation_day] = []
            failures_by_day[f.implementation_day].append(f)
    
    return render_template('implementation/overview.html',
                         days=days,
                         total=total,
                         completed=completed,
                         in_progress=in_progress,
                         blocked=blocked,
                         failures_by_day=failures_by_day)


# Alias so templates using 'implementation.overview' also work
@implementation_bp.route('/overview')
@login_required
def overview():
    return plan_overview()


@implementation_bp.route('/day/<int:day_number>')
@login_required
def day_detail(day_number):
    """View detailed info for a specific implementation day."""
    day = ImplementationDay.query.filter_by(day_number=day_number).first_or_404()
    failures = FailureLog.query.filter_by(implementation_day=day_number).all()
    return render_template('implementation/day_detail.html', day=day, failures=failures)


@implementation_bp.route('/day/<int:day_number>/status', methods=['POST'])
@login_required
def update_day_status(day_number):
    """Update the status of an implementation day."""
    day = ImplementationDay.query.filter_by(day_number=day_number).first_or_404()
    
    data = request.json if request.is_json else request.form
    
    new_status = data.get('status', day.status)
    day.status = new_status
    
    if new_status == 'in_progress' and not day.started_at:
        day.started_at = datetime.now(timezone.utc)
    elif new_status == 'completed':
        day.completed_at = datetime.now(timezone.utc)
    
    if data.get('notes') is not None:
        day.notes = data['notes']
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'day': day.to_dict()})
    
    flash(f'Day {day_number} updated to {new_status}', 'success')
    return redirect(url_for('implementation.day_detail', day_number=day_number))


# Alias so templates using 'implementation.update_day' also work
@implementation_bp.route('/day/<int:day_number>/update', methods=['POST'])
@login_required
def update_day(day_number):
    """Update day status — form-based (from template buttons)."""
    day = ImplementationDay.query.filter_by(day_number=day_number).first_or_404()
    new_status = request.form.get('status', day.status)
    day.status = new_status
    if new_status == 'in_progress' and not day.started_at:
        day.started_at = datetime.now(timezone.utc)
    elif new_status == 'completed':
        day.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f'Day {day_number} updated to {new_status}', 'success')
    return redirect(url_for('implementation.plan_overview'))


@implementation_bp.route('/failure-log', methods=['GET', 'POST'])
@login_required
def failure_log():
    """View and add to the shared failure log."""
    if request.method == 'POST':
        data = request.form if not request.is_json else request.json
        
        failure = FailureLog(
            category=data.get('category', 'other'),
            severity=data.get('severity', 'medium'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            agents_involved=json.dumps(data.get('agents_involved', [])),
            files_involved=json.dumps(data.get('files_involved', [])),
            implementation_day=data.get('implementation_day'),
            reported_by=data.get('reported_by')
        )
        db.session.add(failure)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'failure': failure.to_dict()})
        
        flash('Failure logged', 'info')
        return redirect(url_for('implementation.failure_log'))
    
    failures = FailureLog.query.order_by(FailureLog.timestamp.desc()).all()
    return render_template('implementation/failure_log.html', failures=failures)


# Alias so templates using 'implementation.add_failure' also work
@implementation_bp.route('/failure-log/add', methods=['POST'])
@login_required
def add_failure():
    """Add a failure — redirects to failure_log POST handler."""
    data = request.form if not request.is_json else request.json
    failure = FailureLog(
        category=data.get('category', 'other'),
        severity=data.get('severity', 'medium'),
        title=data.get('title', ''),
        description=data.get('description', ''),
        agents_involved=json.dumps(data.get('agents_involved', [])),
        files_involved=json.dumps(data.get('files_involved', [])),
        implementation_day=data.get('implementation_day'),
        reported_by=data.get('reported_by')
    )
    db.session.add(failure)
    db.session.commit()
    flash('Failure logged', 'info')
    return redirect(url_for('implementation.failure_log'))


@implementation_bp.route('/failure-log/<int:failure_id>/resolve', methods=['POST'])
@login_required
def resolve_failure(failure_id):
    """Mark a failure as resolved."""
    failure = FailureLog.query.get_or_404(failure_id)
    failure.resolved = True
    failure.resolved_at = datetime.now(timezone.utc)
    
    data = request.json if request.is_json else request.form
    failure.resolution = data.get('resolution', '')
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True})
    
    flash('Failure marked as resolved', 'success')
    return redirect(url_for('implementation.failure_log'))
