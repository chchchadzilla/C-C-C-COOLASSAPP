# ═══════════════════════════════════════════════════════════════════════════════
# C-C-C-COOLASSAPP
# ═══════════════════════════════════════════════════════════════════════════════
#
# A comprehensive management platform for teams running 10+ concurrent 
# Claude Code instances. Provides real-time monitoring, user management,
# nightly reports, codebase health tracking, and a 2-week implementation
# strategy with built-in troubleshooting.
#
# Usage:
#   python app.py                    # Start the management server
#   python app.py --port 8080        # Custom port
#   python app.py --debug            # Debug mode
#
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import click
import logging
from datetime import datetime

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# ─── Initialize extensions ────────────────────────────────────────────────────
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    # ─── Configuration ────────────────────────────────────────────────────
    _secret = os.environ.get('SECRET_KEY', '')
    _default_secret = 'claude-orchestration-dev-key-change-in-production'
    if not _secret:
        _secret = _default_secret
        import warnings
        warnings.warn(
            "\n⚠️  SECRET_KEY not set! Using insecure default. "
            "Set SECRET_KEY env var in production.\n"
            "  Windows:  set SECRET_KEY=your-random-secret-here\n"
            "  Linux:    export SECRET_KEY=your-random-secret-here",
            RuntimeWarning, stacklevel=2
        )
    app.config['SECRET_KEY'] = _secret
    app.config['USING_DEFAULT_SECRET'] = (_secret == _default_secret)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///orchestration.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['MAX_AGENTS_PER_USER'] = 10
    app.config['NIGHTLY_REPORT_HOUR'] = 23  # 11 PM
    app.config['NIGHTLY_REPORT_MINUTE'] = 0
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # ─── Initialize extensions ────────────────────────────────────────────
    db.init_app(app)

    # CORS: Read allowed origins from env, default to * only in dev
    _cors_origins = os.environ.get('CORS_ORIGINS', '*')
    if _cors_origins == '*':
        logging.getLogger(__name__).warning(
            "CORS_ORIGINS not set — allowing all origins. "
            "Set CORS_ORIGINS env var in production (comma-separated)."
        )
    else:
        _cors_origins = [o.strip() for o in _cors_origins.split(',') if o.strip()]

    socketio.init_app(app, async_mode='threading', cors_allowed_origins=_cors_origins)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # ─── Custom Jinja filters ────────────────────────────────────────────
    def from_json_filter(value):
        """Parse a JSON string into a Python object."""
        if not value:
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    app.jinja_env.filters['from_json'] = from_json_filter

    # ─── Register blueprints ──────────────────────────────────────────────
    from routes.dashboard import dashboard_bp
    from routes.users import users_bp
    from routes.agents import agents_bp
    from routes.reports import reports_bp
    from routes.implementation import implementation_bp
    from routes.bestpractices import bestpractices_bp
    from routes.health import health_bp
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.settings import settings_bp
    from routes.apikeys import apikeys_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(implementation_bp)
    app.register_blueprint(bestpractices_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(apikeys_bp)
    
    # ─── Create database tables ───────────────────────────────────────────
    with app.app_context():
        from models import User, Agent, AgentSession, Report, ImplementationDay, HealthCheck, FailureLog, ProviderConfig, ApiKey
        db.create_all()
        _seed_implementation_plan(app)
    
    # ─── Setup scheduler for nightly reports ──────────────────────────────
    from services.scheduler import init_scheduler
    init_scheduler(app)
    
    return app


def _seed_implementation_plan(app):
    """Seed the 2-week implementation plan if not already present."""
    from models import ImplementationDay
    if db.session.query(ImplementationDay).count() == 0:
        days = _get_implementation_days()
        for day_data in days:
            day = ImplementationDay(**day_data)
            db.session.add(day)
        db.session.commit()


def _get_implementation_days():
    """Return the 14-day implementation plan data."""
    return [
        {
            "day_number": 1,
            "week": 1,
            "title": "Audit Current Workflow (Part 1)",
            "phase": "Infrastructure & Mindset",
            "description": "Find where people spend the most sequential time. Code review? Testing? Boilerplate? That's where parallelization has the highest immediate ROI.",
            "tasks": json.dumps([
                "Survey each team member on their daily workflow breakdown",
                "Identify top 3 time-consuming sequential tasks per person",
                "Map current code review bottlenecks and average turnaround time",
                "Document current testing workflow and coverage gaps",
                "Measure boilerplate creation time across the team"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Team members can't identify sequential bottlenecks",
                "solution": "Use time-tracking for 2 days. Have everyone log what they're doing in 30-minute blocks. The patterns will emerge.",
                "warning_signs": ["People say 'everything takes long'", "No consensus on biggest bottleneck", "Resistance to tracking time"],
                "escalation": "If the team can't agree on bottlenecks after 2 days of tracking, the orchestrator should make the call based on git commit patterns and PR cycle times."
            }),
            "success_criteria": json.dumps([
                "Clear ranked list of parallelizable tasks",
                "Each team member has identified their top bottleneck",
                "Baseline metrics documented for comparison in Week 2"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 2,
            "week": 1,
            "title": "Audit Current Workflow (Part 2)",
            "phase": "Infrastructure & Mindset",
            "description": "You can't parallelize everything and shouldn't try. Identify what stays sequential and what gets parallelized.",
            "tasks": json.dumps([
                "Create parallelization candidate matrix (task × benefit × risk)",
                "Identify tasks that MUST stay sequential (security reviews, DB migrations)",
                "Calculate expected ROI for top 5 parallelization candidates",
                "Document dependencies between common tasks",
                "Create initial task routing rules (parallel vs sequential)"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Team wants to parallelize everything",
                "solution": "Run a thought experiment: 'What happens if two agents modify the same database migration file?' Help them see that some tasks have inherent ordering requirements.",
                "warning_signs": ["Over-enthusiasm without risk assessment", "Ignoring merge conflict potential", "No dependency mapping"],
                "escalation": "If parallelization scope is too broad, restrict to read-only tasks for the first exercise (Day 5)."
            }),
            "success_criteria": json.dumps([
                "Parallelization matrix completed",
                "Clear separation of parallel-safe vs sequential-only tasks",
                "ROI estimates for top candidates"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 3,
            "week": 1,
            "title": "CLAUDE.md Standards (Part 1)",
            "phase": "Infrastructure & Mindset",
            "description": "Before anyone runs multiple agents, everyone needs a shared standard for context files. One agent with bad context is annoying. Ten agents with bad context is a disaster.",
            "tasks": json.dumps([
                "Review existing CLAUDE.md files across all team repos",
                "Workshop session: team builds CLAUDE.md template together",
                "Define mandatory sections (build commands, test runners, code style)",
                "Define optional sections (domain knowledge, architecture notes)",
                "Create CLAUDE.md linting rules to enforce standards"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Team can't agree on CLAUDE.md format",
                "solution": "Start with the minimal viable template: build commands + test commands + code style. Everything else is optional. Agreement on 3 things is better than disagreement on 20.",
                "warning_signs": ["Bikeshedding on formatting", "CLAUDE.md files over 200 lines", "No testing/verification commands included"],
                "escalation": "The orchestrator picks the template. Democracy is great for buy-in but terrible for deadlines. Pick and iterate."
            }),
            "success_criteria": json.dumps([
                "Team-agreed CLAUDE.md template exists",
                "Template is under 100 lines",
                "Every repo has an updated CLAUDE.md"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 4,
            "week": 1,
            "title": "CLAUDE.md Standards (Part 2)",
            "phase": "Infrastructure & Mindset",
            "description": "Build the template together as a team so there's buy-in. Roll out to all repositories.",
            "tasks": json.dumps([
                "Deploy CLAUDE.md template to all active repositories",
                "Create per-directory CLAUDE.md files for complex repos",
                "Set up skills directory (.claude/skills/) with team conventions",
                "Configure subagent templates (.claude/agents/) for common tasks",
                "Test CLAUDE.md loading with /memory command validation"
            ]),
            "troubleshooting": json.dumps({
                "problem": "CLAUDE.md is too long and Claude ignores instructions",
                "solution": "Split into CLAUDE.md (universal rules) + skill files (domain-specific). Use @imports for structure. Keep root CLAUDE.md under 50 lines.",
                "warning_signs": ["Claude repeatedly ignores documented rules", "Different repos have contradictory standards", "No one validates CLAUDE.md after writing it"],
                "escalation": "If CLAUDE.md bloat persists, implement a pre-commit hook that rejects CLAUDE.md files over the line limit."
            }),
            "success_criteria": json.dumps([
                "All repos have standardized CLAUDE.md",
                "Skills and subagent templates deployed",
                "Team has validated with /memory that context loads correctly"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 5,
            "week": 1,
            "title": "First Parallel Exercise",
            "phase": "Infrastructure & Mindset",
            "description": "Pair programming session where everyone runs exactly 3 agents on a real task. Not a demo. Their actual current work, split three ways.",
            "tasks": json.dumps([
                "Each team member selects a real task from their current backlog",
                "Break the task into 3 independent subtasks",
                "Launch 3 Claude Code sessions simultaneously",
                "Monitor for merge conflicts, context drift, and contradictions",
                "Debrief: document what worked and what created conflicts"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Agents produce conflicting code that can't be merged",
                "solution": "This is expected on first try! The goal is to experience the failure mode. Document the conflict pattern, discuss file-level ownership boundaries for agents.",
                "warning_signs": ["Agents editing the same files", "No clear task boundaries before starting", "People waiting for agents instead of monitoring them"],
                "escalation": "If merge conflicts are severe, reduce to 2 agents and ensure zero file overlap. Add file-locking conventions before scaling to 3."
            }),
            "success_criteria": json.dumps([
                "Every team member has run 3 parallel agents",
                "Conflict log started with real examples",
                "Team identifies top 3 failure patterns"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 6,
            "week": 2,
            "title": "Identify Failure Modes (Part 1)",
            "phase": "Scaling & Failure Modes",
            "description": "10 parallel agents will create problems you don't have with 1. Merge conflicts, contradictory implementations, context drift.",
            "tasks": json.dumps([
                "Catalog all failure modes from Day 5 exercise",
                "Classify failures: merge conflicts, context drift, contradictions, resource contention",
                "Create shared failure log accessible to entire team",
                "Assign severity levels to each failure type",
                "Begin documenting mitigation strategies for each category"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Team is discouraged by number of failures",
                "solution": "Reframe: failures at 3 agents are cheap lessons. The same failures at 10 agents would be expensive. This is the entire point of the exercise.",
                "warning_signs": ["Team wants to go back to single agent", "Failures not being documented", "Same failure happening repeatedly without mitigation"],
                "escalation": "If morale is low, show concrete time savings from the successful parallel tasks. Even 50% success rate at 3x speed is a net win."
            }),
            "success_criteria": json.dumps([
                "Comprehensive failure catalog created",
                "Each failure has a severity level",
                "Mitigation strategies drafted for top 5 failures"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 7,
            "week": 2,
            "title": "Identify Failure Modes (Part 2)",
            "phase": "Scaling & Failure Modes",
            "description": "Document every failure in a shared log so the team is learning collectively, not just individually.",
            "tasks": json.dumps([
                "Scale exercise to 5 agents per person",
                "Implement file-ownership boundaries for parallel work",
                "Test context drift detection: compare agent outputs for consistency",
                "Practice merge conflict resolution workflows",
                "Update failure log with new patterns from 5-agent exercise"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Context drift - agents make contradictory architectural decisions",
                "solution": "Strengthen CLAUDE.md with explicit architectural decisions. Use subagents with read-only permissions for review tasks. Ensure all agents share the same context baseline.",
                "warning_signs": ["Agent A uses pattern X while Agent B uses pattern Y for same thing", "Inconsistent naming conventions across parallel outputs", "Agents not reading CLAUDE.md properly"],
                "escalation": "Implement a 'consistency checker' agent that reviews all parallel outputs before merge."
            }),
            "success_criteria": json.dumps([
                "5 agents running without critical failures",
                "File ownership boundaries are working",
                "Context drift detection process in place"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 8,
            "week": 2,
            "title": "Identify Failure Modes (Part 3)",
            "phase": "Scaling & Failure Modes",
            "description": "Final failure mode identification. Scale to 7 agents and stress-test the mitigation strategies.",
            "tasks": json.dumps([
                "Scale to 7 agents with mitigation strategies active",
                "Test cross-agent coordination for complex features",
                "Validate that conflict resolution workflow handles 7-agent load",
                "Measure token usage patterns and cost projections at scale",
                "Finalize failure mode documentation with resolution playbooks"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Token costs are higher than expected at 7 agents",
                "solution": "Implement agent specialization: read-only review agents use less context. Use /compact aggressively. Ensure agents aren't re-reading files that haven't changed.",
                "warning_signs": ["Agents doing redundant file reads", "Context windows filling up before task completion", "Cost per task increasing non-linearly"],
                "escalation": "Set per-agent token budgets. Kill agents that exceed budget and reassign to a fresh session with better scoping."
            }),
            "success_criteria": json.dumps([
                "7 agents running with acceptable failure rate (<15%)",
                "Token cost projections documented",
                "All major failure modes have resolution playbooks"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 9,
            "week": 2,
            "title": "Build Orchestration Layer (Part 1)",
            "phase": "Scaling & Failure Modes",
            "description": "Define which task types get parallelized by default, which stay sequential, and who owns conflict resolution.",
            "tasks": json.dumps([
                "Formalize task routing rules into configuration",
                "Define default parallelization policies per task type",
                "Create conflict resolution ownership matrix",
                "Build agent assignment templates for common workflows",
                "Set up automated merge conflict detection and alerting"
            ]),
            "troubleshooting": json.dumps({
                "problem": "No one wants to own conflict resolution",
                "solution": "This isn't a technical problem — it's a workflow governance problem. Assign conflict resolution to the person who owns the feature, not a random team member. Feature owners are conflict resolvers.",
                "warning_signs": ["Conflicts piling up without resolution", "Unclear ownership causing delays", "Team treating conflicts as bugs instead of workflow issues"],
                "escalation": "Designate a daily rotating 'merge master' role until the team builds muscle memory for conflict resolution."
            }),
            "success_criteria": json.dumps([
                "Task routing rules formalized and documented",
                "Conflict resolution ownership assigned",
                "Automated conflict detection active"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 10,
            "week": 2,
            "title": "Build Orchestration Layer (Part 2)",
            "phase": "Scaling & Failure Modes",
            "description": "This isn't a technical problem — it's a workflow governance problem. Finalize the orchestration processes.",
            "tasks": json.dumps([
                "Implement the orchestration dashboard monitoring",
                "Configure nightly report generation",
                "Set up codebase health checks (lint, tests, coverage)",
                "Create runbook for common orchestration failures",
                "Test full orchestration flow with 8 agents"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Orchestration overhead negating parallelization benefits",
                "solution": "If orchestration is taking more time than it saves, you're over-managing. Simplify: fewer rules, more trust in the agents, faster feedback loops. The goal is 80% automation, 20% oversight.",
                "warning_signs": ["More time managing agents than doing work", "Excessive approval workflows", "Dashboard monitoring becoming a full-time job"],
                "escalation": "Cut orchestration rules in half. Keep only the ones that prevent data loss or broken builds."
            }),
            "success_criteria": json.dumps([
                "Dashboard showing real-time agent status",
                "Nightly reports generating correctly",
                "Full orchestration flow validated at 8 agents"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 11,
            "week": 2,
            "title": "Full Deployment (Day 1)",
            "phase": "Full Deployment with Checkpoints",
            "description": "Everyone running target load. Begin daily 15-minute standups specifically about agent orchestration.",
            "tasks": json.dumps([
                "Scale all team members to 10 agents",
                "First orchestration standup (15 min max)",
                "Monitor for new failure modes at full scale",
                "Track per-person adaptation curve",
                "Begin collecting nightly report data"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Some team members struggling with 10 agents",
                "solution": "Not everyone will get the orchestrator mindset immediately. Let struggling members run 5-7 agents while adapting. The plan has to account for different learning speeds.",
                "warning_signs": ["Agent sessions timing out unused", "Quality of parallel output dropping", "Team member anxiety about losing control"],
                "escalation": "Pair the struggling member with someone who's adapted. Buddy system for 2-3 days, then re-evaluate."
            }),
            "success_criteria": json.dumps([
                "Majority of team at 10 agents",
                "First standup completed",
                "No critical failures in first hours"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 12,
            "week": 2,
            "title": "Full Deployment (Day 2)",
            "phase": "Full Deployment with Checkpoints",
            "description": "Daily standup about agent orchestration — not code, not product. Just what broke, what worked, what changed.",
            "tasks": json.dumps([
                "Second orchestration standup",
                "Review first nightly report with team",
                "Adjust agent count per person based on performance",
                "Refine task routing based on Day 11 data",
                "Update failure log and resolution playbooks"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Standups turning into general dev discussions",
                "solution": "Strict agenda: 1) What orchestration issue did you hit? 2) How did you resolve it? 3) What would you change? No product discussion. No code review. Pure orchestration.",
                "warning_signs": ["Standups exceeding 15 minutes", "Discussion drifting to features", "People not prepared with orchestration-specific updates"],
                "escalation": "Written async updates instead of standups. Some teams communicate better in writing."
            }),
            "success_criteria": json.dumps([
                "Standup stayed on topic and under 15 min",
                "Nightly report reviewed and actionable insights identified",
                "Agent counts adjusted where needed"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 13,
            "week": 2,
            "title": "Full Deployment (Day 3)",
            "phase": "Full Deployment with Checkpoints",
            "description": "Focus on stabilization. Address any systemic issues and optimize individual workflows.",
            "tasks": json.dumps([
                "Third orchestration standup",
                "Identify any systemic issues across the team",
                "Optimize individual agent configurations per developer",
                "Run codebase health check - compare to Day 1 baseline",
                "Document team-wide patterns and anti-patterns"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Codebase quality declining despite agent productivity",
                "solution": "Add a dedicated review agent to every parallel workflow. One agent writes, one reviews. The review agent catches what the writer misses. Net cost: ~30% more tokens. Net benefit: dramatically fewer bugs merging.",
                "warning_signs": ["Test coverage dropping", "Lint errors increasing", "PR rejection rate going up"],
                "escalation": "Temporarily reduce to 8 agents per person and add mandatory CI gate checks before any agent output is merged."
            }),
            "success_criteria": json.dumps([
                "No systemic degradation from baseline",
                "Individual optimizations documented",
                "Patterns and anti-patterns catalog shared"
            ]),
            "status": "not_started"
        },
        {
            "day_number": 14,
            "week": 2,
            "title": "Full Deployment (Day 4) — Retrospective",
            "phase": "Full Deployment with Checkpoints",
            "description": "You're not a developer using a tool anymore. You're an orchestrator managing a team. Final checkpoint and retrospective.",
            "tasks": json.dumps([
                "Final orchestration standup",
                "Full 2-week retrospective (60 min)",
                "Compare baseline metrics to current performance",
                "Document the team's orchestration playbook",
                "Set ongoing orchestration cadence (weekly check-in, monthly review)",
                "Celebrate wins and acknowledge the mindset shift"
            ]),
            "troubleshooting": json.dumps({
                "problem": "Results don't match expectations",
                "solution": "10 parallel agents in 2 weeks is achievable technically. The harder problem is the mindset shift. If metrics improved even 30%, that's a win worth building on. Perfection is the enemy of progress.",
                "warning_signs": ["Team comparing to theoretical 10x instead of actual improvement", "Focus on failures instead of wins", "No clear path for continued improvement"],
                "escalation": "Extend the ramp-up by 1 more week. Some teams need 3 weeks instead of 2. That's not failure — that's being realistic about adoption curves."
            }),
            "success_criteria": json.dumps([
                "2-week retrospective completed",
                "Orchestration playbook documented",
                "Ongoing cadence established",
                "Team aligned on next iteration goals"
            ]),
            "status": "not_started"
        }
    ]

@click.command()
@click.option('--port', default=5000, help='Port to run the server on')
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def main(port, host, debug):
    """Start the C-C-C-COOLASSAPP."""
    app = create_app()
    
    print(r"""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   🤖 C-C-C-COOLASSAPP                 ║
    ║                                                                   ║
    ║   Dashboard:  http://localhost:{port}                             ║
    ║   API Docs:   http://localhost:{port}/api                         ║
    ║                                                                   ║
    ║   Managing up to 10 concurrent Claude Code instances per user     ║
    ║   Real-time monitoring • Nightly reports • Health checks          ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """.format(port=port))
    
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
