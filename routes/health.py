# ═══════════════════════════════════════════════════════════════════════════════
# CODEBASE HEALTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from datetime import datetime, timezone
from app import db
from models import HealthCheck

health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/')
@login_required
def overview():
    """Codebase health overview."""
    checks = HealthCheck.query.order_by(HealthCheck.check_date.desc()).limit(30).all()
    latest = checks[0] if checks else None
    return render_template('health/overview.html', checks=checks, latest=latest)


@health_bp.route('/run-check', methods=['POST'])
@login_required
def run_check():
    """Run a new health check."""
    from services.health_checker import run_health_check
    check = run_health_check()
    return jsonify({'success': True, 'check': check.to_dict()})


@health_bp.route('/history')
@login_required
def history():
    """Health check history with trends."""
    checks = HealthCheck.query.order_by(HealthCheck.check_date.desc()).limit(100).all()
    return render_template('health/history.html', checks=checks)
