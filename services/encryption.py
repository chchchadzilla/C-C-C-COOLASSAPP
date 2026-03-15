# ═══════════════════════════════════════════════════════════════════════════════
# ENCRYPTION SERVICE — Secure API key storage
# ═══════════════════════════════════════════════════════════════════════════════
#
# Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256) derived from
# the Flask SECRET_KEY.  Keys are encrypted at rest in SQLite and decrypted
# only when needed for an outbound API call.
#
# ═══════════════════════════════════════════════════════════════════════════════

import base64
import hashlib
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# Module-level cache so we don't re-derive on every call
_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """Return a Fernet instance derived from the Flask SECRET_KEY."""
    global _fernet
    if _fernet is not None:
        return _fernet

    from flask import current_app
    secret = current_app.config['SECRET_KEY']
    # Derive a 32-byte key via SHA-256, then base64-encode for Fernet
    derived = hashlib.sha256(secret.encode('utf-8')).digest()
    key = base64.urlsafe_b64encode(derived)
    _fernet = Fernet(key)
    return _fernet


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string → URL-safe base64 ciphertext.
    Returns empty string if input is empty.
    """
    if not plaintext:
        return ''
    try:
        f = _get_fernet()
        token = f.encrypt(plaintext.encode('utf-8'))
        return token.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_value(ciphertext: str) -> str:
    """
    Decrypt a ciphertext string → original plaintext.
    Returns empty string if input is empty.
    """
    if not ciphertext:
        return ''
    try:
        f = _get_fernet()
        plaintext = f.decrypt(ciphertext.encode('utf-8'))
        return plaintext.decode('utf-8')
    except InvalidToken:
        logger.error("Decryption failed — invalid token (wrong SECRET_KEY?)")
        return ''
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ''


def mask_key(plaintext: str) -> str:
    """
    Return a masked version of an API key for display.
    Shows the first 4 and last 4 characters with dots in between.
    e.g. "sk-ant-abc123...xyz789"
    """
    if not plaintext:
        return '(not set)'
    if len(plaintext) <= 10:
        return plaintext[:2] + '•' * (len(plaintext) - 2)
    return plaintext[:6] + '•' * 8 + plaintext[-4:]


def is_encrypted(value: str) -> bool:
    """
    Heuristic check: Fernet tokens start with 'gAAAAA'.
    Helps distinguish already-encrypted values from raw keys.
    """
    if not value:
        return False
    return value.startswith('gAAAAA')
