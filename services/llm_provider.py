# ═══════════════════════════════════════════════════════════════════════════════
# LLM PROVIDER SERVICE — Multi-backend abstraction layer
# ═══════════════════════════════════════════════════════════════════════════════
#
# Supports:
#   - Claude Code (local CLI subprocess)
#   - Anthropic API (direct HTTP)
#   - OpenRouter (unified gateway)
#   - GitHub Copilot (chat completions)
#
# Usage:
#   from services.llm_provider import send_message, test_provider_connection
#   response = send_message(provider_id, messages=[...])
#
# ═══════════════════════════════════════════════════════════════════════════════

import json
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Per-User Key Resolution ─────────────────────────────────────────────────

# Maps provider_type strings from ProviderConfig → ApiKey.provider_type
_PROVIDER_TO_APIKEY_TYPE = {
    'anthropic': 'anthropic',
    'openrouter': 'openrouter',
    'github_copilot': 'github_copilot',
    'claude_code': None,  # Uses local CLI, no API key needed
}


def _resolve_api_key(provider_config, user=None) -> Optional[str]:
    """
    Resolve the API key to use for a request.

    Priority:
      1. Per-user key from the ApiKey table (if user is provided)
      2. Shared key from the ProviderConfig
      3. None (will fail downstream)

    Also updates usage tracking on the per-user key.
    """
    # Map provider type to ApiKey provider_type
    apikey_type = _PROVIDER_TO_APIKEY_TYPE.get(provider_config.provider_type)

    # Try per-user key first
    if user and apikey_type:
        try:
            from models import ApiKey
            user_key = ApiKey.query.filter_by(
                user_id=user.id,
                provider_type=apikey_type,
                is_active=True,
                is_valid=True
            ).first()
            if user_key:
                decrypted = user_key.get_key()
                if decrypted:
                    logger.debug(f"Using per-user key for {user.username}/{apikey_type}")
                    return decrypted
        except Exception as e:
            logger.warning(f"Failed to look up per-user key: {e}")

    # Fall back to shared provider key (decrypt from Fernet ciphertext)
    return provider_config.get_api_key()


def _track_key_usage(provider_config, user, tokens_used: int = 0):
    """Update usage stats on the per-user key after a successful call."""
    if not user:
        return
    apikey_type = _PROVIDER_TO_APIKEY_TYPE.get(provider_config.provider_type)
    if not apikey_type:
        return
    try:
        from models import ApiKey, db
        from datetime import datetime, timezone
        user_key = ApiKey.query.filter_by(
            user_id=user.id,
            provider_type=apikey_type,
            is_active=True
        ).first()
        if user_key:
            user_key.total_requests = (user_key.total_requests or 0) + 1
            user_key.total_tokens = (user_key.total_tokens or 0) + tokens_used
            user_key.last_used_at = datetime.now(timezone.utc)
            user_key.last_error = None  # Clear any previous error
            db.session.commit()
    except Exception as e:
        logger.warning(f"Failed to track key usage: {e}")


# ─── Public API ───────────────────────────────────────────────────────────────

def send_message(provider_config, messages: list, model: str = None,
                 max_tokens: int = None, temperature: float = None,
                 user=None) -> dict:
    """
    Send a message to the configured LLM provider.

    Args:
        provider_config: ProviderConfig model instance
        messages: List of {"role": "...", "content": "..."} dicts
        model: Override model (falls back to provider default)
        max_tokens: Override max tokens
        temperature: Override temperature
        user: Optional User model instance for per-user key resolution

    Returns:
        {"content": str, "model": str, "tokens_used": int, "provider": str}
    """
    ptype = provider_config.provider_type
    model = model or provider_config.default_model
    max_tokens = max_tokens or provider_config.max_tokens
    temperature = temperature if temperature is not None else provider_config.temperature

    # Resolve the API key (per-user first, then shared provider key)
    resolved_key = _resolve_api_key(provider_config, user)

    dispatch = {
        'claude_code': _send_claude_code,
        'anthropic': _send_anthropic,
        'openrouter': _send_openrouter,
        'github_copilot': _send_github_copilot,
    }

    handler = dispatch.get(ptype)
    if not handler:
        raise ValueError(f"Unknown provider type: {ptype}")

    result = handler(provider_config, messages, model, max_tokens, temperature,
                     api_key=resolved_key)

    # Track usage on the per-user key
    _track_key_usage(provider_config, user, result.get('tokens_used', 0))

    return result


def test_provider_connection(provider_config) -> tuple:
    """
    Test a provider connection with a minimal request.
    Returns (success: bool, message: str).
    """
    ptype = provider_config.provider_type

    try:
        if ptype == 'claude_code':
            return _test_claude_code(provider_config)
        elif ptype == 'anthropic':
            return _test_anthropic(provider_config)
        elif ptype == 'openrouter':
            return _test_openrouter(provider_config)
        elif ptype == 'github_copilot':
            return _test_github_copilot(provider_config)
        else:
            return False, f"Unknown provider type: {ptype}"
    except Exception as e:
        logger.exception(f"Provider test failed for {provider_config.name}")
        return False, str(e)


def get_default_provider():
    """Return the default ProviderConfig, or the first enabled one."""
    from models import ProviderConfig
    provider = ProviderConfig.query.filter_by(is_default=True, is_enabled=True).first()
    if not provider:
        provider = ProviderConfig.query.filter_by(is_enabled=True).order_by(
            ProviderConfig.priority
        ).first()
    return provider


def list_available_models() -> list:
    """Return a flat list of models from all enabled providers."""
    from models import ProviderConfig
    providers = ProviderConfig.query.filter_by(is_enabled=True).order_by(
        ProviderConfig.priority
    ).all()
    models = []
    for p in providers:
        meta = ProviderConfig.PROVIDER_TYPES.get(p.provider_type, {})
        for m in meta.get('default_models', []):
            entry = f"{p.name}: {m}"
            if entry not in models:
                models.append(entry)
        if p.default_model:
            entry = f"{p.name}: {p.default_model}"
            if entry not in models:
                models.append(entry)
    return models


# ─── Claude Code (local CLI) ─────────────────────────────────────────────────

def _send_claude_code(config, messages, model, max_tokens, temperature, api_key=None):
    """Execute via the `claude` CLI tool (local subprocess)."""
    # Build the prompt from the last user message
    prompt = messages[-1]['content'] if messages else ''

    cmd = ['claude', '--print', '--model', model]
    if max_tokens:
        cmd += ['--max-tokens', str(max_tokens)]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=config.working_directory or None,  # Dedicated CWD field
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI error: {result.stderr.strip()}")

        return {
            'content': result.stdout.strip(),
            'model': model,
            'tokens_used': 0,  # CLI doesn't report tokens
            'provider': config.name,
        }
    except FileNotFoundError:
        raise RuntimeError("'claude' CLI not found — ensure Claude Code is installed and on PATH")


def _test_claude_code(config):
    """Test that the claude CLI is accessible."""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"Claude CLI available: {version}"
        return False, f"CLI returned code {result.returncode}: {result.stderr.strip()}"
    except FileNotFoundError:
        return False, "'claude' not found on PATH"
    except Exception as e:
        return False, str(e)


# ─── Anthropic API ────────────────────────────────────────────────────────────

def _send_anthropic(config, messages, model, max_tokens, temperature, api_key=None):
    """Call Anthropic Messages API directly."""
    import urllib.request

    base = config.api_base_url or 'https://api.anthropic.com'
    url = f"{base}/v1/messages"

    # Use resolved key (per-user or shared)
    key = api_key or config.get_api_key()

    # Convert to Anthropic format: separate system from user/assistant
    system_text = ''
    api_messages = []
    for m in messages:
        if m['role'] == 'system':
            system_text += m['content'] + '\n'
        else:
            api_messages.append({'role': m['role'], 'content': m['content']})

    payload = {
        'model': model,
        'max_tokens': max_tokens,
        'messages': api_messages,
    }
    if system_text.strip():
        payload['system'] = system_text.strip()
    if temperature > 0:
        payload['temperature'] = temperature

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    content = ''
    for block in data.get('content', []):
        if block.get('type') == 'text':
            content += block['text']

    usage = data.get('usage', {})
    return {
        'content': content,
        'model': data.get('model', model),
        'tokens_used': usage.get('input_tokens', 0) + usage.get('output_tokens', 0),
        'provider': config.name,
    }


def _test_anthropic(config):
    """Test Anthropic API key with a minimal request."""
    if not config.api_key:
        return False, "No API key configured"
    try:
        result = _send_anthropic(
            config,
            [{'role': 'user', 'content': 'Reply with exactly: OK'}],
            config.default_model or 'claude-3-5-haiku-20241022',
            16, 0,
            api_key=config.get_api_key(),
        )
        return True, f"Connected — model: {result['model']}"
    except Exception as e:
        return False, str(e)


# ─── OpenRouter ───────────────────────────────────────────────────────────────

def _send_openrouter(config, messages, model, max_tokens, temperature, api_key=None):
    """Call OpenRouter chat completions API."""
    import urllib.request

    base = config.api_base_url or 'https://openrouter.ai/api'
    url = f"{base}/v1/chat/completions"

    # Use resolved key (per-user or shared)
    key = api_key or config.get_api_key()

    payload = {
        'model': model,
        'max_tokens': max_tokens,
        'messages': [{'role': m['role'], 'content': m['content']} for m in messages],
    }
    if temperature > 0:
        payload['temperature'] = temperature

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}',
        'HTTP-Referer': 'https://claude-orchestrator.local',
        'X-Title': 'C-C-C-COOLASSAPP',
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    choice = data.get('choices', [{}])[0]
    message = choice.get('message', {})
    usage = data.get('usage', {})

    return {
        'content': message.get('content', ''),
        'model': data.get('model', model),
        'tokens_used': usage.get('total_tokens', 0),
        'provider': config.name,
    }


def _test_openrouter(config):
    """Test OpenRouter connection."""
    if not config.api_key:
        return False, "No API key configured"
    try:
        result = _send_openrouter(
            config,
            [{'role': 'user', 'content': 'Reply with exactly: OK'}],
            config.default_model or 'anthropic/claude-3.5-haiku',
            16, 0,
            api_key=config.get_api_key(),
        )
        return True, f"Connected — model: {result['model']}"
    except Exception as e:
        return False, str(e)


# ─── GitHub Copilot ───────────────────────────────────────────────────────────

def _send_github_copilot(config, messages, model, max_tokens, temperature, api_key=None):
    """Call GitHub Copilot chat completions endpoint."""
    import urllib.request

    # Copilot uses a token-based auth flow
    # The api_key here is the GitHub token (ghu_ or gho_ or classic PAT)
    base = config.api_base_url or 'https://api.githubcopilot.com'
    url = f"{base}/chat/completions"

    # Use resolved key (per-user or shared)
    key = api_key or config.get_api_key()

    payload = {
        'model': model,
        'max_tokens': max_tokens,
        'messages': [{'role': m['role'], 'content': m['content']} for m in messages],
    }
    if temperature > 0:
        payload['temperature'] = temperature

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}',
        'Editor-Version': 'Claude-Orchestrator/1.0',
        'Copilot-Integration-Id': 'claude-orchestrator',
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    choice = data.get('choices', [{}])[0]
    message = choice.get('message', {})
    usage = data.get('usage', {})

    return {
        'content': message.get('content', ''),
        'model': data.get('model', model),
        'tokens_used': usage.get('total_tokens', 0),
        'provider': config.name,
    }


def _test_github_copilot(config):
    """Test GitHub Copilot token validity."""
    if not config.api_key:
        return False, "No token configured"
    try:
        # Try a simple auth check against GitHub API first
        import urllib.request
        decrypted_key = config.get_api_key()
        req = urllib.request.Request(
            'https://api.github.com/user',
            headers={'Authorization': f'Bearer {decrypted_key}', 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        username = data.get('login', 'unknown')
        return True, f"Authenticated as @{username}"
    except Exception as e:
        return False, f"GitHub auth failed: {e}"
