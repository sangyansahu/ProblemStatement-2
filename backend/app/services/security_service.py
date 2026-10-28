import hmac
import hashlib
import re
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from flask import current_app

def get_hmac_secret() -> bytes:
    secret = current_app.config.get('APAAR_HMAC_SECRET', 'aicte-hmac-salt-apaar-2026-strict-key')
    return secret.encode('utf-8')

def get_cipher():
    raw_key = current_app.config.get('APAAR_ENCRYPTION_KEY', 'J7mZ8pQwK3rL1sXvY9uNtF2gH4dE6jA8bC0eG2iK4mU=')
    # Fernet requires a 32-byte url-safe base64 encoded key
    if len(raw_key) != 44:
        # Derive 32 bytes from SHA256 then b64encode
        digest = hashlib.sha256(raw_key.encode('utf-8')).digest()
        key = urlsafe_b64encode(digest)
    else:
        key = raw_key.encode('utf-8')
    return Fernet(key)

def clean_apaar_id(raw_apaar: str) -> str:
    if not raw_apaar:
        return ''
    # Remove whitespace, dashes, slashes
    cleaned = re.sub(r'[\s\-_]', '', str(raw_apaar).strip())
    return cleaned

def validate_apaar_format(raw_apaar: str) -> tuple[bool, str]:
    if not raw_apaar:
        return False, "APAAR ID is missing or empty"
    cleaned = clean_apaar_id(raw_apaar)
    if not cleaned.isdigit():
        return False, f"APAAR ID must contain only digits, found: {raw_apaar}"
    if len(cleaned) != 12:
        return False, f"APAAR ID must be exactly 12 digits, found {len(cleaned)} digits"
    return True, cleaned

def generate_apaar_hmac(cleaned_apaar: str) -> str:
    """Computes keyed HMAC-SHA256 for privacy-preserving equality matching and duplicate detection."""
    if not cleaned_apaar:
        return None
    secret = get_hmac_secret()
    h = hmac.new(secret, cleaned_apaar.encode('utf-8'), hashlib.sha256)
    return h.hexdigest()

def mask_apaar(raw_apaar: str) -> str:
    """Masks APAAR ID to protect student privacy: e.g. APAAR-****-****-4821"""
    if not raw_apaar:
        return "Not Assigned"
    cleaned = clean_apaar_id(raw_apaar)
    if len(cleaned) == 12:
        return f"APAAR-****-****-{cleaned[-4:]}"
    if len(cleaned) >= 4:
        return f"APAAR-****-{cleaned[-4:]}"
    return "APAAR-****"

def encrypt_apaar(cleaned_apaar: str) -> str:
    """Encrypts APAAR identifier with AES-256 for secure storage."""
    if not cleaned_apaar:
        return None
    cipher = get_cipher()
    encrypted = cipher.encrypt(cleaned_apaar.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_apaar(encrypted_token: str) -> str:
    """Decrypts APAAR identifier when authorized by Super Admin."""
    if not encrypted_token:
        return None
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_token.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception:
        return None
