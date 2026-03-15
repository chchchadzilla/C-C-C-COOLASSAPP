# ═══════════════════════════════════════════════════════════════════════════════
# OPENROUTER MODELS SERVICE — Fetches real model list from OpenRouter API
# ═══════════════════════════════════════════════════════════════════════════════
#
# Uses GET https://openrouter.ai/api/v1/models (no auth required)
# Caches results in memory with a 5-minute TTL to avoid hammering the API.
#
# ═══════════════════════════════════════════════════════════════════════════════

import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# ─── In-memory cache ──────────────────────────────────────────────────────────
_cache: dict = {
    'models': [],       # list of model dicts
    'fetched_at': 0.0,  # timestamp of last fetch
}
_CACHE_TTL = 300  # 5 minutes

OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'


def _fetch_models_from_api() -> list[dict]:
    """Hit the OpenRouter /api/v1/models endpoint and return raw model list."""
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=15, headers={
            'Accept': 'application/json',
        })
        resp.raise_for_status()
        data = resp.json()
        models = data.get('data', [])
        logger.info(f"Fetched {len(models)} models from OpenRouter API")
        return models
    except requests.RequestException as e:
        logger.error(f"Failed to fetch OpenRouter models: {e}")
        return []


def get_openrouter_models(force_refresh: bool = False) -> list[dict]:
    """
    Return the cached list of OpenRouter models, refreshing if stale.

    Each model dict has at minimum:
        id, name, context_length, pricing, architecture, description
    """
    now = time.time()
    if not force_refresh and _cache['models'] and (now - _cache['fetched_at'] < _CACHE_TTL):
        return _cache['models']

    models = _fetch_models_from_api()
    if models:
        _cache['models'] = models
        _cache['fetched_at'] = now
    # If fetch failed but we have stale data, keep serving stale
    return _cache['models']


def get_openrouter_model_ids(force_refresh: bool = False) -> list[str]:
    """Return just the model ID strings, sorted by name for the dropdown."""
    models = get_openrouter_models(force_refresh)
    # Sort by human-readable name
    models_sorted = sorted(models, key=lambda m: m.get('name', m['id']).lower())
    return [m['id'] for m in models_sorted]


def get_openrouter_models_for_dropdown(force_refresh: bool = False) -> list[dict]:
    """
    Return a compact list suitable for a UI dropdown.

    Each entry:
        {
            'id':             'anthropic/claude-sonnet-4',
            'name':           'Anthropic: Claude Sonnet 4',
            'context_length': 200000,
            'pricing': {
                'prompt':     '0.000003',
                'completion': '0.000015',
            },
            'modality':       'text+image->text',
        }
    """
    models = get_openrouter_models(force_refresh)

    dropdown = []
    for m in models:
        pricing = m.get('pricing', {})
        arch = m.get('architecture', {})
        dropdown.append({
            'id': m['id'],
            'name': m.get('name', m['id']),
            'context_length': m.get('context_length', 0),
            'pricing': {
                'prompt': pricing.get('prompt', '0'),
                'completion': pricing.get('completion', '0'),
            },
            'modality': arch.get('modality', ''),
        })

    # Sort: alphabetical by name
    dropdown.sort(key=lambda m: m['name'].lower())
    return dropdown
