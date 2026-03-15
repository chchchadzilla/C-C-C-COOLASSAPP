# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS & PROVIDER CONFIGURATION ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from models import ProviderConfig

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _admin_required(f):
    """Decorator: only admin or orchestrator can manage providers."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('admin', 'orchestrator'):
            flash('Insufficient permissions', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ─── Provider listing ─────────────────────────────────────────────────────────

@settings_bp.route('/')
@login_required
@_admin_required
def index():
    """Provider settings dashboard."""
    providers = ProviderConfig.query.order_by(ProviderConfig.priority).all()
    provider_types = ProviderConfig.PROVIDER_TYPES
    return render_template('settings/index.html',
                           providers=providers,
                           provider_types=provider_types)


# ─── Create provider ─────────────────────────────────────────────────────────

@settings_bp.route('/providers/create', methods=['GET', 'POST'])
@login_required
@_admin_required
def create_provider():
    """Add a new LLM provider configuration."""
    if request.method == 'POST':
        provider_type = request.form.get('provider_type', '')
        if provider_type not in ProviderConfig.PROVIDER_TYPES:
            flash('Invalid provider type', 'error')
            return redirect(url_for('settings.index'))

        make_default = request.form.get('is_default') == 'on'

        # If making this the default, unset the current default
        if make_default:
            ProviderConfig.query.filter_by(is_default=True).update({'is_default': False})

        provider = ProviderConfig(
            name=request.form.get('name', '').strip(),
            provider_type=provider_type,
            api_key=request.form.get('api_key', '').strip(),
            api_base_url=request.form.get('api_base_url', '').strip(),
            org_id=request.form.get('org_id', '').strip(),
            default_model=request.form.get('default_model', '').strip(),
            max_tokens=int(request.form.get('max_tokens', 4096)),
            temperature=float(request.form.get('temperature', 0.0)),
            is_enabled=request.form.get('is_enabled') == 'on',
            is_default=make_default,
            priority=int(request.form.get('priority', 0)),
            created_by=current_user.id,
        )
        db.session.add(provider)
        db.session.commit()

        flash(f'Provider "{provider.name}" created', 'success')
        return redirect(url_for('settings.index'))

    provider_types = ProviderConfig.PROVIDER_TYPES
    return render_template('settings/create.html', provider_types=provider_types)


# ─── Edit provider ───────────────────────────────────────────────────────────

@settings_bp.route('/providers/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
@_admin_required
def edit_provider(provider_id):
    """Edit an existing provider configuration."""
    provider = ProviderConfig.query.get_or_404(provider_id)

    if request.method == 'POST':
        provider.name = request.form.get('name', provider.name).strip()
        provider.api_base_url = request.form.get('api_base_url', '').strip()
        provider.org_id = request.form.get('org_id', '').strip()
        provider.default_model = request.form.get('default_model', '').strip()
        provider.max_tokens = int(request.form.get('max_tokens', 4096))
        provider.temperature = float(request.form.get('temperature', 0.0))
        provider.is_enabled = request.form.get('is_enabled') == 'on'
        provider.priority = int(request.form.get('priority', 0))

        # Only update key if a new one was submitted (don't blank on empty)
        new_key = request.form.get('api_key', '').strip()
        if new_key:
            provider.api_key = new_key

        make_default = request.form.get('is_default') == 'on'
        if make_default and not provider.is_default:
            ProviderConfig.query.filter_by(is_default=True).update({'is_default': False})
            provider.is_default = True
        elif not make_default:
            provider.is_default = False

        db.session.commit()
        flash(f'Provider "{provider.name}" updated', 'success')
        return redirect(url_for('settings.index'))

    provider_types = ProviderConfig.PROVIDER_TYPES
    return render_template('settings/edit.html',
                           provider=provider,
                           provider_types=provider_types)


# ─── Delete provider ─────────────────────────────────────────────────────────

@settings_bp.route('/providers/<int:provider_id>/delete', methods=['POST'])
@login_required
@_admin_required
def delete_provider(provider_id):
    """Remove a provider configuration."""
    provider = ProviderConfig.query.get_or_404(provider_id)
    name = provider.name
    db.session.delete(provider)
    db.session.commit()
    flash(f'Provider "{name}" deleted', 'warning')
    return redirect(url_for('settings.index'))


# ─── Toggle enable/disable ───────────────────────────────────────────────────

@settings_bp.route('/providers/<int:provider_id>/toggle', methods=['POST'])
@login_required
@_admin_required
def toggle_provider(provider_id):
    """Toggle a provider on/off."""
    provider = ProviderConfig.query.get_or_404(provider_id)
    provider.is_enabled = not provider.is_enabled
    db.session.commit()

    status = 'enabled' if provider.is_enabled else 'disabled'
    if request.is_json:
        return jsonify({'success': True, 'is_enabled': provider.is_enabled})
    flash(f'Provider "{provider.name}" {status}', 'success')
    return redirect(url_for('settings.index'))


# ─── Test connection ──────────────────────────────────────────────────────────

@settings_bp.route('/providers/<int:provider_id>/test', methods=['POST'])
@login_required
@_admin_required
def test_provider(provider_id):
    """Test a provider connection by sending a minimal request."""
    provider = ProviderConfig.query.get_or_404(provider_id)

    try:
        from services.llm_provider import test_provider_connection
        ok, message = test_provider_connection(provider)
        provider.last_tested_at = datetime.now(timezone.utc)
        provider.last_test_status = 'ok' if ok else 'error'
        provider.last_test_message = message
        db.session.commit()

        if request.is_json:
            return jsonify({'success': ok, 'message': message})
        flash(f'Test {"passed" if ok else "failed"}: {message}', 'success' if ok else 'error')
    except Exception as e:
        provider.last_tested_at = datetime.now(timezone.utc)
        provider.last_test_status = 'error'
        provider.last_test_message = str(e)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        flash(f'Test error: {e}', 'error')

    return redirect(url_for('settings.index'))


# ─── API: list available models for a provider type ──────────────────────────

@settings_bp.route('/api/models/<provider_type>')
@login_required
def api_models(provider_type):
    """Return available models for a provider type (used by JS dropdowns)."""
    meta = ProviderConfig.PROVIDER_TYPES.get(provider_type, {})

    # For OpenRouter: fetch real models from their API
    if provider_type == 'openrouter':
        from services.openrouter_models import get_openrouter_models_for_dropdown
        dropdown = get_openrouter_models_for_dropdown()
        model_ids = [m['id'] for m in dropdown]
        return jsonify({
            'models': model_ids,
            'models_detail': dropdown,
            'meta': meta,
            'source': 'live',
        })

    # Other providers: use hardcoded defaults
    models = list(meta.get('default_models', []))

    # Also pull any custom models from existing configs of this type
    configs = ProviderConfig.query.filter_by(
        provider_type=provider_type, is_enabled=True
    ).all()
    for cfg in configs:
        if cfg.default_model and cfg.default_model not in models:
            models.append(cfg.default_model)

    return jsonify({'models': models, 'meta': meta})


# ─── API: all enabled providers + their models (for agent create form) ───────

@settings_bp.route('/api/enabled-providers')
@login_required
def api_enabled_providers():
    """Return all enabled providers with their model lists."""
    providers = ProviderConfig.query.filter_by(is_enabled=True).order_by(
        ProviderConfig.priority
    ).all()

    # Pre-fetch OpenRouter models once if any provider uses it
    _openrouter_ids = None
    if any(p.provider_type == 'openrouter' for p in providers):
        from services.openrouter_models import get_openrouter_model_ids
        _openrouter_ids = get_openrouter_model_ids()

    result = []
    for p in providers:
        meta = ProviderConfig.PROVIDER_TYPES.get(p.provider_type, {})

        if p.provider_type == 'openrouter' and _openrouter_ids:
            models = list(_openrouter_ids)
        else:
            models = list(meta.get('default_models', []))

        if p.default_model and p.default_model not in models:
            models.insert(0, p.default_model)

        result.append({
            'id': p.id,
            'name': p.name,
            'provider_type': p.provider_type,
            'icon': meta.get('icon', '🔌'),
            'default_model': p.default_model,
            'models': models,
            'is_default': p.is_default,
        })
    return jsonify({'providers': result})
