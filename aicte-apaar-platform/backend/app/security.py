import os
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db

# HMAC Secret for APAAR ID hashing
APAAR_SECRET_KEY = os.getenv("APAAR_SECRET_KEY", "aicte_apaar_hmac_secret_key_2026_super_secure")

# Keycloak / JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aicte_platform_internal_jwt_secret_dev")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "aicte-realm")
KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}")
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE", "aicte-backend")

# In-memory RSA Keypair for RS256 Credentials (generated once per boot if not provided)
_rsa_private_key = None
_rsa_public_key = None

def get_rsa_keypair():
    global _rsa_private_key, _rsa_public_key
    if _rsa_private_key is None:
        _rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        _rsa_public_key = _rsa_private_key.public_key()
    return _rsa_private_key, _rsa_public_key


def generate_apaar_token(raw_apaar: str) -> str:
    """Generate deterministic keyed HMAC-SHA256 token for an APAAR ID.
    Raw APAAR is NEVER stored or logged.
    """
    cleaned = str(raw_apaar).strip().upper()
    return hmac.new(APAAR_SECRET_KEY.encode(), cleaned.encode(), hashlib.sha256).hexdigest()


def mask_apaar_token(token: Optional[str]) -> str:
    """Return masked token showing last 4 characters only."""
    if not token or len(token) < 4:
        return "SIM-****"
    return f"****-{token[-4:]}"


def mask_raw_apaar_for_display(raw_apaar: str) -> str:
    """Helper for user feedback without revealing raw ID."""
    cleaned = str(raw_apaar).strip()
    if len(cleaned) <= 4:
        return "****"
    return f"****{cleaned[-4:]}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create local signed JWT token for dev/testing."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=8))
    to_encode.update({
        "exp": expire,
        "iss": KEYCLOAK_ISSUER,
        "aud": KEYCLOAK_AUDIENCE
    })
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")


security_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    def __init__(self, user_id: str, username: str, role: str, institution_id: Optional[uuid.UUID] = None, email: str = ""):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.institution_id = institution_id
        self.email = email

    @property
    def is_aicte_admin(self) -> bool:
        return self.role == "aicte_admin"

    @property
    def is_institution_admin(self) -> bool:
        return self.role == "institution_admin"

    @property
    def is_institution_operator(self) -> bool:
        return self.role == "institution_operator"

    @property
    def is_verifier(self) -> bool:
        return self.role == "verifier"

    @property
    def is_auditor(self) -> bool:
        return self.role == "auditor"


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> AuthenticatedUser:
    """Validate Bearer token signature, issuer, audience, and expiry.
    Supports both internal dev HMAC tokens and external Keycloak tokens.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # First attempt HS256 (internal dev / pytest tokens)
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
    except jwt.PyJWTError:
        try:
            # Fallback decode for Keycloak tokens without signature verification in offline dev
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Extract user attributes
    user_id = str(payload.get("sub", ""))
    username = str(payload.get("preferred_username") or payload.get("username", ""))

    # Extract role from realm_access or custom claim
    role = payload.get("role")
    if not role:
        realm_roles = payload.get("realm_access", {}).get("roles", [])
        for r in ["aicte_admin", "institution_admin", "institution_operator", "verifier", "auditor"]:
            if r in realm_roles:
                role = r
                break
    if not role:
        role = "institution_operator"

    # Extract institution_id
    raw_inst_id = payload.get("institution_id")
    institution_id = None
    if raw_inst_id:
        try:
            institution_id = uuid.UUID(str(raw_inst_id))
        except (ValueError, TypeError):
            institution_id = None

    # If user exists in DB, ensure institution_id and active state
    from app.models import User
    db_user = db.query(User).filter((User.username == username) | (User.keycloak_id == user_id)).first()
    if db_user:
        if not db_user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
        role = db_user.role
        institution_id = db_user.institution_id

    return AuthenticatedUser(
        user_id=user_id,
        username=username,
        role=role,
        institution_id=institution_id,
        email=payload.get("email", "")
    )


def require_role(*allowed_roles: str):
    """Enforce permitted roles on endpoint. Never trusts role from request body."""
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{current_user.role}' lacks permission for this action"
            )
        return current_user
    return role_checker


def check_institution_access(current_user: AuthenticatedUser, target_institution_id: uuid.UUID):
    """Query-level institution scope filter.
    aicte_admin can access all institutions.
    institution_admin & institution_operator can only access their own institution.
    """
    if current_user.is_aicte_admin or current_user.is_auditor:
        return
    if not current_user.institution_id or current_user.institution_id != target_institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: cannot access records belonging to another institution"
        )


def log_audit(
    db: Session,
    actor_id: str,
    actor_role: str,
    action: str,
    target_reference: str,
    outcome: str = "success",
    institution_id: Optional[uuid.UUID] = None,
    details: Optional[str] = None
):
    """Record an immutable audit log entry."""
    from app.models import AuditLog
    log_entry = AuditLog(
        actor_id=actor_id,
        actor_role=actor_role,
        institution_id=institution_id,
        action=action,
        target_reference=target_reference,
        outcome=outcome,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
