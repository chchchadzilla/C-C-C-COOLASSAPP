# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

import json
from datetime import datetime, timezone
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """A team member who manages Claude Code instances."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='developer')  # admin, orchestrator, developer
    max_agents = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)  # Force password change on first login
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    agents = db.relationship('Agent', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    # Week 1-2 tracking
    current_agent_count = db.Column(db.Integer, default=0)
    target_agent_count = db.Column(db.Integer, default=3)  # Starts at 3 (Day 5), scales to 10
    adaptation_score = db.Column(db.Float, default=0.0)  # 0-100 how well they're adapting
    notes = db.Column(db.Text, default='')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'max_agents': self.max_agents,
            'is_active': self.is_active,
            'current_agent_count': self.current_agent_count,
            'target_agent_count': self.target_agent_count,
            'adaptation_score': self.adaptation_score,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }


class Agent(db.Model):
    """A Claude Code instance assigned to a user."""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "agent-01"
    name = db.Column(db.String(120), nullable=False)  # e.g., "API Builder"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status tracking
    status = db.Column(db.String(20), default='idle')  # idle, active, error, paused, terminated
    current_task = db.Column(db.Text, default='')
    current_branch = db.Column(db.String(200), default='')
    current_files = db.Column(db.Text, default='[]')  # JSON array of files being worked on
    
    # Agent configuration
    agent_type = db.Column(db.String(50), default='general')  # general, reviewer, tester, writer, researcher
    permission_mode = db.Column(db.String(30), default='default')  # default, permissive, readonly, sandbox
    model = db.Column(db.String(50), default='sonnet')
    
    # Performance metrics
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_failed = db.Column(db.Integer, default=0)
    merge_conflicts = db.Column(db.Integer, default=0)
    tokens_used = db.Column(db.Integer, default=0)
    session_count = db.Column(db.Integer, default=0)
    avg_task_duration_minutes = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime, nullable=True)
    
    # Sessions
    sessions = db.relationship('AgentSession', backref='agent', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_current_files(self):
        try:
            return json.loads(self.current_files)
        except:
            return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'user_id': self.user_id,
            'status': self.status,
            'current_task': self.current_task,
            'current_branch': self.current_branch,
            'current_files': self.get_current_files(),
            'agent_type': self.agent_type,
            'permission_mode': self.permission_mode,
            'model': self.model,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'merge_conflicts': self.merge_conflicts,
            'tokens_used': self.tokens_used,
            'session_count': self.session_count,
            'avg_task_duration_minutes': self.avg_task_duration_minutes,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AgentSession(db.Model):
    """A record of a Claude Code session."""
    __tablename__ = 'agent_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    
    # Session details
    task_description = db.Column(db.Text, default='')
    branch_name = db.Column(db.String(200), default='')
    files_modified = db.Column(db.Text, default='[]')
    
    # Outcomes
    status = db.Column(db.String(20), default='running')  # running, completed, failed, aborted
    outcome_summary = db.Column(db.Text, default='')
    log_output = db.Column(db.Text, default='')  # JSON: {stdout, stderr, exit_code}
    merge_conflicts = db.Column(db.Integer, default=0)
    tests_passed = db.Column(db.Integer, default=0)
    tests_failed = db.Column(db.Integer, default=0)
    tokens_used = db.Column(db.Integer, default=0)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'task_description': self.task_description,
            'branch_name': self.branch_name,
            'files_modified': json.loads(self.files_modified) if self.files_modified else [],
            'status': self.status,
            'outcome_summary': self.outcome_summary,
            'log_output': json.loads(self.log_output) if self.log_output else {},
            'merge_conflicts': self.merge_conflicts,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'tokens_used': self.tokens_used,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.duration_minutes
        }


class Report(db.Model):
    """Nightly performance reports."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False)
    report_type = db.Column(db.String(30), default='nightly')  # nightly, weekly, custom
    
    # Aggregate metrics
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_tasks_failed = db.Column(db.Integer, default=0)
    total_merge_conflicts = db.Column(db.Integer, default=0)
    total_tokens_used = db.Column(db.Integer, default=0)
    active_agents = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    
    # Quality metrics
    avg_task_success_rate = db.Column(db.Float, default=0.0)
    codebase_health_score = db.Column(db.Float, default=0.0)
    test_coverage_delta = db.Column(db.Float, default=0.0)
    lint_errors_delta = db.Column(db.Integer, default=0)
    
    # Per-user breakdown (JSON)
    user_breakdown = db.Column(db.Text, default='{}')
    
    # Problems and highlights
    problems_solved = db.Column(db.Text, default='[]')
    merge_conflict_details = db.Column(db.Text, default='[]')
    highlights = db.Column(db.Text, default='[]')
    recommendations = db.Column(db.Text, default='[]')
    
    # Generated report content
    report_html = db.Column(db.Text, default='')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'report_type': self.report_type,
            'total_tasks_completed': self.total_tasks_completed,
            'total_tasks_failed': self.total_tasks_failed,
            'total_merge_conflicts': self.total_merge_conflicts,
            'total_tokens_used': self.total_tokens_used,
            'active_agents': self.active_agents,
            'active_users': self.active_users,
            'avg_task_success_rate': self.avg_task_success_rate,
            'codebase_health_score': self.codebase_health_score,
            'problems_solved': json.loads(self.problems_solved) if self.problems_solved else [],
            'merge_conflict_details': json.loads(self.merge_conflict_details) if self.merge_conflict_details else [],
            'highlights': json.loads(self.highlights) if self.highlights else [],
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ImplementationDay(db.Model):
    """2-week implementation plan tracker."""
    __tablename__ = 'implementation_days'
    
    id = db.Column(db.Integer, primary_key=True)
    day_number = db.Column(db.Integer, nullable=False, unique=True)
    week = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    phase = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tasks = db.Column(db.Text, default='[]')  # JSON array
    troubleshooting = db.Column(db.Text, default='{}')  # JSON object
    success_criteria = db.Column(db.Text, default='[]')  # JSON array
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, blocked
    notes = db.Column(db.Text, default='')
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_number': self.day_number,
            'week': self.week,
            'title': self.title,
            'phase': self.phase,
            'description': self.description,
            'tasks': json.loads(self.tasks) if self.tasks else [],
            'troubleshooting': json.loads(self.troubleshooting) if self.troubleshooting else {},
            'success_criteria': json.loads(self.success_criteria) if self.success_criteria else [],
            'status': self.status,
            'notes': self.notes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class HealthCheck(db.Model):
    """Codebase health check results."""
    __tablename__ = 'health_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    check_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Git health
    total_branches = db.Column(db.Integer, default=0)
    stale_branches = db.Column(db.Integer, default=0)
    unmerged_prs = db.Column(db.Integer, default=0)
    merge_conflicts_active = db.Column(db.Integer, default=0)
    
    # Code quality
    lint_errors = db.Column(db.Integer, default=0)
    lint_warnings = db.Column(db.Integer, default=0)
    test_coverage_pct = db.Column(db.Float, default=0.0)
    tests_passing = db.Column(db.Integer, default=0)
    tests_failing = db.Column(db.Integer, default=0)
    
    # Context health  
    claude_md_files = db.Column(db.Integer, default=0)
    claude_md_avg_lines = db.Column(db.Float, default=0.0)
    skills_count = db.Column(db.Integer, default=0)
    agents_defined = db.Column(db.Integer, default=0)
    
    # Overall score
    health_score = db.Column(db.Float, default=0.0)  # 0-100
    details = db.Column(db.Text, default='{}')
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_date': self.check_date.isoformat() if self.check_date else None,
            'total_branches': self.total_branches,
            'stale_branches': self.stale_branches,
            'unmerged_prs': self.unmerged_prs,
            'merge_conflicts_active': self.merge_conflicts_active,
            'lint_errors': self.lint_errors,
            'test_coverage_pct': self.test_coverage_pct,
            'tests_passing': self.tests_passing,
            'tests_failing': self.tests_failing,
            'claude_md_files': self.claude_md_files,
            'claude_md_avg_lines': self.claude_md_avg_lines,
            'health_score': self.health_score,
            'details': json.loads(self.details) if self.details else {}
        }


class FailureLog(db.Model):
    """Shared failure log for the team."""
    __tablename__ = 'failure_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Failure details
    category = db.Column(db.String(50), nullable=False)  # merge_conflict, context_drift, contradiction, resource, other
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Resolution
    resolution = db.Column(db.Text, default='')
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Context
    agents_involved = db.Column(db.Text, default='[]')  # JSON array of agent IDs
    files_involved = db.Column(db.Text, default='[]')  # JSON array of file paths
    implementation_day = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'reported_by': self.reported_by,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'resolution': self.resolution,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'agents_involved': json.loads(self.agents_involved) if self.agents_involved else [],
            'files_involved': json.loads(self.files_involved) if self.files_involved else [],
            'implementation_day': self.implementation_day
        }


class ProviderConfig(db.Model):
    """LLM provider configuration — supports multiple backends."""
    __tablename__ = 'provider_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # User-friendly label
    provider_type = db.Column(db.String(30), nullable=False)
    # Provider types: claude_code, anthropic, openrouter, github_copilot

    # Connection
    api_key = db.Column(db.String(512), default='')  # Encrypted via Fernet
    api_base_url = db.Column(db.String(512), default='')  # Custom endpoint override
    org_id = db.Column(db.String(200), default='')  # Org header for some providers
    working_directory = db.Column(db.String(512), default='')  # CWD for Claude CLI

    # Defaults
    default_model = db.Column(db.String(120), default='')
    max_tokens = db.Column(db.Integer, default=4096)
    temperature = db.Column(db.Float, default=0.0)

    # State
    is_enabled = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)  # Lower = higher priority for fallback

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    last_tested_at = db.Column(db.DateTime, nullable=True)
    last_test_status = db.Column(db.String(20), default='untested')  # untested, ok, error
    last_test_message = db.Column(db.Text, default='')

    # Provider-specific metadata (JSON)
    extra_config = db.Column(db.Text, default='{}')

    # Class-level constants for dropdowns / validation
    PROVIDER_TYPES = {
        'claude_code': {
            'label': 'Claude Code (Local CLI)',
            'icon': '🖥️',
            'needs_key': False,
            'default_models': ['claude-sonnet-4-20250514', 'claude-opus-4-20250514'],
        },
        'anthropic': {
            'label': 'Anthropic API',
            'icon': '🔮',
            'needs_key': True,
            'default_models': ['claude-sonnet-4-20250514', 'claude-opus-4-20250514',
                               'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022'],
        },
        'openrouter': {
            'label': 'OpenRouter',
            'icon': '🌐',
            'needs_key': True,
            'default_models': ['anthropic/claude-sonnet-4', 'anthropic/claude-opus-4',
                               'google/gemini-2.5-pro', 'openai/gpt-4.1',
                               'deepseek/deepseek-r1', 'meta-llama/llama-4-maverick'],
        },
        'github_copilot': {
            'label': 'GitHub Copilot',
            'icon': '🐙',
            'needs_key': True,
            'default_models': ['claude-sonnet-4', 'gpt-4.1', 'claude-opus-4', 'o4-mini'],
        },
    }

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider_type': self.provider_type,
            'api_base_url': self.api_base_url,
            'org_id': self.org_id,
            'default_model': self.default_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'is_enabled': self.is_enabled,
            'is_default': self.is_default,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_tested_at': self.last_tested_at.isoformat() if self.last_tested_at else None,
            'last_test_status': self.last_test_status,
            'last_test_message': self.last_test_message,
            'has_key': bool(self.api_key),
            'provider_meta': self.PROVIDER_TYPES.get(self.provider_type, {}),
        }

    # ── Encrypted key helpers ─────────────────────────────────────────────
    def set_api_key(self, raw_key: str):
        """Encrypt and store an API key via Fernet."""
        from services.encryption import encrypt_value
        self.api_key = encrypt_value(raw_key) if raw_key else ''

    def get_api_key(self) -> str:
        """Decrypt and return the stored API key."""
        from services.encryption import decrypt_value, is_encrypted
        if not self.api_key:
            return ''
        # If the value is already Fernet ciphertext, decrypt it
        if is_encrypted(self.api_key):
            return decrypt_value(self.api_key)
        # Legacy plaintext key — return as-is (will be encrypted on next save)
        return self.api_key

    def get_key_hint(self) -> str:
        """Return a masked key hint for UI placeholders."""
        from services.encryption import mask_key
        raw = self.get_api_key()
        return mask_key(raw) if raw else ''


class ApiKey(db.Model):
    """
    Per-user API key storage — encrypted at rest.

    Each user can store one key per provider type.  Admins can view / manage
    all keys.  The raw key is encrypted via services.encryption before being
    written and decrypted only when needed for an outbound call.
    """
    __tablename__ = 'api_keys'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'provider_type', name='uq_user_provider'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_type = db.Column(db.String(30), nullable=False)
    # Provider types: anthropic, openrouter, github_copilot
    # (claude_code doesn't need a key — it's local CLI)

    # The key itself — stored as Fernet ciphertext
    encrypted_key = db.Column(db.Text, default='')

    # Human-friendly label (e.g. "My work Anthropic key")
    label = db.Column(db.String(200), default='')

    # Masking info (stored so we don't need to decrypt just to show UI)
    key_hint = db.Column(db.String(50), default='')  # e.g. "sk-ant-a•••••bc12"

    # State
    is_active = db.Column(db.Boolean, default=True)
    is_valid = db.Column(db.Boolean, default=True)  # Set to False if key fails

    # Usage tracking
    total_requests = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)
    last_error = db.Column(db.Text, default='')

    # Audit
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref=db.backref('api_keys', lazy='dynamic',
                                                       cascade='all, delete-orphan'))

    # Class-level provider info
    PROVIDER_CHOICES = {
        'anthropic': {
            'label': 'Anthropic API Key',
            'icon': '🔮',
            'prefix_hint': 'sk-ant-...',
            'help_url': 'https://console.anthropic.com/settings/keys',
            'placeholder': 'sk-ant-api03-...',
        },
        'openrouter': {
            'label': 'OpenRouter API Key',
            'icon': '🌐',
            'prefix_hint': 'sk-or-...',
            'help_url': 'https://openrouter.ai/keys',
            'placeholder': 'sk-or-v1-...',
        },
        'github_copilot': {
            'label': 'GitHub Copilot Token',
            'icon': '🐙',
            'prefix_hint': 'ghu_... / ghp_...',
            'help_url': 'https://github.com/settings/tokens',
            'placeholder': 'ghp_...',
        },
    }

    def set_key(self, raw_key: str):
        """Encrypt and store a raw API key, updating the hint."""
        from services.encryption import encrypt_value, mask_key
        self.encrypted_key = encrypt_value(raw_key)
        self.key_hint = mask_key(raw_key)

    def get_key(self) -> str:
        """Decrypt and return the raw API key."""
        from services.encryption import decrypt_value
        return decrypt_value(self.encrypted_key)

    def to_dict(self, include_hint=True, admin=False):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'provider_type': self.provider_type,
            'label': self.label,
            'is_active': self.is_active,
            'is_valid': self.is_valid,
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'provider_meta': self.PROVIDER_CHOICES.get(self.provider_type, {}),
        }
        if include_hint:
            d['key_hint'] = self.key_hint
        return d
