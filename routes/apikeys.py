# ═══════════════════════════════════════════════════════════════════════════════
# API KEY MANAGEMENT ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Per-user encrypted API key storage with admin oversight.
#
# User routes:
#   GET  /api-keys/                        — list my keys
#   GET  /api-keys/add                     — add key form
#   POST /api-keys/add                     — save new key
#   GET  /api-keys/<id>/edit               — edit key form
#   POST /api-keys/<id>/edit               — update key
#   POST /api-keys/<id>/delete             — delete key
#   POST /api-keys/<id>/test               — test a key
#   POST /api-keys/<id>/toggle             — enable/disable
#
# Admin routes:
#   GET  /api-keys/admin                   — view all users' keys
#   POST /api-keys/admin/<id>/revoke       — revoke a user's key
#   POST /api-keys/admin/<id>/activate     — re-activate a key
#
# API (JSON) routes:
#   GET  /api-keys/check/<provider_type>   — does current user have this key?
#   POST /api-keys/prompt-save             — save key from the modal prompt
#   GET  /api-keys/api/user-keys           — JSON list of current user's keys
#
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from functools import wraps

from app import db
from models import ApiKey, User

apikeys_bp = Blueprint('apikeys', __name__, url_prefix='/api-keys')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _admin_required(f):
    """Only admin or orchestrator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('admin', 'orchestrator'):
            flash('Insufficient permissions', 'error')
            return redirect(url_for('apikeys.my_keys'))
        return f(*args, **kwargs)
    return decorated


def _test_key(api_key_obj) -> tuple:
    """
    Test an API key by making a minimal request to its provider.
    Returns (success: bool, message: str).
    """
    raw = api_key_obj.get_key()
    if not raw:
        return False, 'No key stored'

    ptype = api_key_obj.provider_type
    try:
        if ptype == 'anthropic':
            return _test_anthropic_key(raw)
        elif ptype == 'openrouter':
            return _test_openrouter_key(raw)
        elif ptype == 'github_copilot':
            return _test_github_key(raw)
        else:
            return False, f'Unknown provider type: {ptype}'
    except Exception as e:
        return False, str(e)


def _test_anthropic_key(key: str) -> tuple:
    import urllib.request, json
    url = 'https://api.anthropic.com/v1/messages'
    payload = {
        'model': 'claude-3-5-haiku-20241022',
        'max_tokens': 8,
        'messages': [{'role': 'user', 'content': 'Reply OK'}],
    }
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        model = data.get('model', '?')
        return True, f'Valid — responded with model {model}'
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return False, f'HTTP {e.code}: {body[:200]}'


def _test_openrouter_key(key: str) -> tuple:
    import urllib.request, json
    url = 'https://openrouter.ai/api/v1/auth/key'
    headers = {'Authorization': f'Bearer {key}'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        label = data.get('data', {}).get('label', 'unknown')
        return True, f'Valid — key label: {label}'
    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}'


def _test_github_key(key: str) -> tuple:
    import urllib.request, json
    url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {key}', 'Accept': 'application/json'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        login = data.get('login', '?')
        return True, f'Valid — GitHub user: {login}'
    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}'


# ═══════════════════════════════════════════════════════════════════════════════
#  USER ROUTES — manage your own keys
# ═══════════════════════════════════════════════════════════════════════════════

@apikeys_bp.route('/')
@login_required
def my_keys():
    """List current user's API keys."""
    keys = ApiKey.query.filter_by(user_id=current_user.id).order_by(ApiKey.provider_type).all()
    provider_choices = ApiKey.PROVIDER_CHOICES
    # Figure out which providers the user still needs to add
    existing_types = {k.provider_type for k in keys}
    missing_types = {t: v for t, v in provider_choices.items() if t not in existing_types}
    return render_template('apikeys/index.html',
                           keys=keys,
                           provider_choices=provider_choices,
                           missing_types=missing_types)


@apikeys_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_key():
    """Add a new API key."""
    if request.method == 'POST':
        provider_type = request.form.get('provider_type', '')
        raw_key = request.form.get('api_key', '').strip()
        label = request.form.get('label', '').strip()

        if provider_type not in ApiKey.PROVIDER_CHOICES:
            flash('Invalid provider type', 'error')
            return redirect(url_for('apikeys.my_keys'))

        if not raw_key:
            flash('API key cannot be empty', 'error')
            return redirect(url_for('apikeys.add_key'))

        # Check if the user already has a key for this provider
        existing = ApiKey.query.filter_by(
            user_id=current_user.id, provider_type=provider_type
        ).first()
        if existing:
            flash(f'You already have a key for {provider_type}. Edit the existing one.', 'warning')
            return redirect(url_for('apikeys.edit_key', key_id=existing.id))

        key_obj = ApiKey(
            user_id=current_user.id,
            provider_type=provider_type,
            label=label or ApiKey.PROVIDER_CHOICES[provider_type]['label'],
        )
        key_obj.set_key(raw_key)
        db.session.add(key_obj)
        db.session.commit()

        flash(f'API key saved securely', 'success')
        return redirect(url_for('apikeys.my_keys'))

    provider_choices = ApiKey.PROVIDER_CHOICES
    # Filter out providers the user already has
    existing = {k.provider_type for k in
                ApiKey.query.filter_by(user_id=current_user.id).all()}
    available = {t: v for t, v in provider_choices.items() if t not in existing}

    preselect = request.args.get('provider', '')
    return render_template('apikeys/add.html',
                           provider_choices=available,
                           preselect=preselect)


@apikeys_bp.route('/<int:key_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_key(key_id):
    """Edit an existing API key."""
    key_obj = ApiKey.query.get_or_404(key_id)

    # Users can only edit their own keys (admins can via admin view)
    if key_obj.user_id != current_user.id and current_user.role not in ('admin', 'orchestrator'):
        flash('You can only edit your own keys', 'error')
        return redirect(url_for('apikeys.my_keys'))

    if request.method == 'POST':
        new_key = request.form.get('api_key', '').strip()
        label = request.form.get('label', '').strip()

        if label:
            key_obj.label = label

        if new_key:
            key_obj.set_key(new_key)
            key_obj.is_valid = True  # Reset validity on new key
            key_obj.last_error = ''

        db.session.commit()
        flash('API key updated', 'success')
        return redirect(url_for('apikeys.my_keys'))

    provider_meta = ApiKey.PROVIDER_CHOICES.get(key_obj.provider_type, {})
    return render_template('apikeys/edit.html', key=key_obj, provider_meta=provider_meta)


@apikeys_bp.route('/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_key(key_id):
    """Delete an API key."""
    key_obj = ApiKey.query.get_or_404(key_id)
    if key_obj.user_id != current_user.id and current_user.role not in ('admin', 'orchestrator'):
        flash('You can only delete your own keys', 'error')
        return redirect(url_for('apikeys.my_keys'))

    provider = key_obj.provider_type
    db.session.delete(key_obj)
    db.session.commit()
    flash(f'{provider} key deleted', 'warning')
    return redirect(url_for('apikeys.my_keys'))


@apikeys_bp.route('/<int:key_id>/test', methods=['POST'])
@login_required
def test_key(key_id):
    """Test an API key against its provider."""
    key_obj = ApiKey.query.get_or_404(key_id)
    if key_obj.user_id != current_user.id and current_user.role not in ('admin', 'orchestrator'):
        flash('You can only test your own keys', 'error')
        return redirect(url_for('apikeys.my_keys'))

    ok, message = _test_key(key_obj)
    key_obj.is_valid = ok
    key_obj.last_error = '' if ok else message
    db.session.commit()

    if request.is_json:
        return jsonify({'success': ok, 'message': message})

    flash(f'Key test {"passed ✓" if ok else "failed ✗"}: {message}',
          'success' if ok else 'error')
    return redirect(url_for('apikeys.my_keys'))


@apikeys_bp.route('/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_key(key_id):
    """Enable/disable an API key."""
    key_obj = ApiKey.query.get_or_404(key_id)
    if key_obj.user_id != current_user.id and current_user.role not in ('admin', 'orchestrator'):
        flash('Permission denied', 'error')
        return redirect(url_for('apikeys.my_keys'))

    key_obj.is_active = not key_obj.is_active
    db.session.commit()

    status = 'enabled' if key_obj.is_active else 'disabled'
    if request.is_json:
        return jsonify({'success': True, 'is_active': key_obj.is_active})
    flash(f'Key {status}', 'success')
    return redirect(url_for('apikeys.my_keys'))


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES — manage all users' keys
# ═══════════════════════════════════════════════════════════════════════════════

@apikeys_bp.route('/admin')
@login_required
@_admin_required
def admin_keys():
    """Admin view: all API keys across all users."""
    keys = (ApiKey.query
            .join(User, ApiKey.user_id == User.id)
            .order_by(User.username, ApiKey.provider_type)
            .all())
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    provider_choices = ApiKey.PROVIDER_CHOICES
    return render_template('apikeys/admin.html',
                           keys=keys,
                           users=users,
                           provider_choices=provider_choices)


@apikeys_bp.route('/admin/<int:key_id>/revoke', methods=['POST'])
@login_required
@_admin_required
def admin_revoke_key(key_id):
    """Admin: deactivate a user's key."""
    key_obj = ApiKey.query.get_or_404(key_id)
    key_obj.is_active = False
    db.session.commit()
    flash(f'Key for {key_obj.user.display_name} ({key_obj.provider_type}) revoked', 'warning')
    return redirect(url_for('apikeys.admin_keys'))


@apikeys_bp.route('/admin/<int:key_id>/activate', methods=['POST'])
@login_required
@_admin_required
def admin_activate_key(key_id):
    """Admin: re-activate a user's key."""
    key_obj = ApiKey.query.get_or_404(key_id)
    key_obj.is_active = True
    db.session.commit()
    flash(f'Key for {key_obj.user.display_name} ({key_obj.provider_type}) re-activated', 'success')
    return redirect(url_for('apikeys.admin_keys'))


@apikeys_bp.route('/admin/<int:key_id>/delete', methods=['POST'])
@login_required
@_admin_required
def admin_delete_key(key_id):
    """Admin: permanently delete a user's key."""
    key_obj = ApiKey.query.get_or_404(key_id)
    name = f'{key_obj.user.display_name} / {key_obj.provider_type}'
    db.session.delete(key_obj)
    db.session.commit()
    flash(f'Key for {name} permanently deleted', 'warning')
    return redirect(url_for('apikeys.admin_keys'))


@apikeys_bp.route('/admin/<int:key_id>/reveal', methods=['POST'])
@login_required
@_admin_required
def admin_reveal_key(key_id):
    """Admin: decrypt and reveal a user's key (JSON only, logged)."""
    key_obj = ApiKey.query.get_or_404(key_id)
    import logging
    logging.getLogger('audit').warning(
        f'Admin {current_user.username} revealed API key #{key_id} '
        f'belonging to user #{key_obj.user_id} ({key_obj.provider_type})'
    )
    raw = key_obj.get_key()
    return jsonify({'key': raw, 'provider': key_obj.provider_type})


# ═══════════════════════════════════════════════════════════════════════════════
#  API ROUTES — used by frontend JS / modal prompt
# ═══════════════════════════════════════════════════════════════════════════════

@apikeys_bp.route('/check/<provider_type>')
@login_required
def check_key(provider_type):
    """
    Check if the current user has an active key for this provider.
    Returns JSON: { has_key: bool, key_hint: str }
    Used by the frontend to decide whether to show the API key prompt modal.
    """
    key_obj = ApiKey.query.filter_by(
        user_id=current_user.id,
        provider_type=provider_type,
        is_active=True
    ).first()
    return jsonify({
        'has_key': key_obj is not None,
        'is_valid': key_obj.is_valid if key_obj else False,
        'key_hint': key_obj.key_hint if key_obj else '',
    })


@apikeys_bp.route('/prompt-save', methods=['POST'])
@login_required
def prompt_save():
    """
    Save an API key from the modal prompt (AJAX endpoint).
    Accepts JSON: { provider_type, api_key, label? }
    """
    data = request.json if request.is_json else request.form
    provider_type = data.get('provider_type', '')
    raw_key = data.get('api_key', '').strip()
    label = data.get('label', '').strip()

    if provider_type not in ApiKey.PROVIDER_CHOICES:
        return jsonify({'success': False, 'error': 'Invalid provider type'}), 400
    if not raw_key:
        return jsonify({'success': False, 'error': 'API key is required'}), 400

    # Upsert: update existing or create new
    key_obj = ApiKey.query.filter_by(
        user_id=current_user.id, provider_type=provider_type
    ).first()

    if key_obj:
        key_obj.set_key(raw_key)
        key_obj.is_valid = True
        key_obj.is_active = True
        key_obj.last_error = ''
        if label:
            key_obj.label = label
    else:
        key_obj = ApiKey(
            user_id=current_user.id,
            provider_type=provider_type,
            label=label or ApiKey.PROVIDER_CHOICES[provider_type]['label'],
        )
        key_obj.set_key(raw_key)
        db.session.add(key_obj)

    db.session.commit()
    return jsonify({'success': True, 'key_hint': key_obj.key_hint})


@apikeys_bp.route('/api/user-keys')
@login_required
def api_user_keys():
    """JSON list of current user's keys (for frontend components)."""
    keys = ApiKey.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'keys': [k.to_dict() for k in keys],
        'providers': ApiKey.PROVIDER_CHOICES,
    })
