# ═══════════════════════════════════════════════════════════════════════════════
# BEST PRACTICES ROUTES — Claude Code tips, tricks, and patterns
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template
from flask_login import login_required

bestpractices_bp = Blueprint('bestpractices', __name__, url_prefix='/best-practices')


@bestpractices_bp.route('/')
@login_required
def index():
    """Best practices knowledge base."""
    return render_template('bestpractices/index.html')


@bestpractices_bp.route('/claude-md')
@login_required
def claude_md():
    """CLAUDE.md writing guide and templates."""
    return render_template('bestpractices/claude_md.html')


@bestpractices_bp.route('/parallel-agents')
@login_required
def parallel_agents():
    """Guide to running parallel agents effectively."""
    return render_template('bestpractices/parallel_agents.html')


@bestpractices_bp.route('/failure-modes')
@login_required
def failure_modes():
    """Common failure modes and mitigations."""
    return render_template('bestpractices/failure_modes.html')


@bestpractices_bp.route('/orchestration-patterns')
@login_required
def orchestration_patterns():
    """Orchestration workflow patterns."""
    return render_template('bestpractices/orchestration_patterns.html')


@bestpractices_bp.route('/commands')
@login_required
def commands():
    """Essential Claude Code commands reference."""
    return render_template('bestpractices/commands.html')
