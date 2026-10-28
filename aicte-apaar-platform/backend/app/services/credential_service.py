import uuid
import secrets
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
from cryptography.hazmat.primitives import serialization
import qrcode
from sqlalchemy.orm import Session
from app.models import Credential, Student, Admission, Institution
from app.security import get_rsa_keypair


def generate_opaque_reference() -> str:
    """Generate cryptographically random opaque verification token."""
    return f"CR-{secrets.token_urlsafe(16)}"


def issue_student_credential(
    db: Session,
    admission_id: uuid.UUID,
    institution_id: uuid.UUID,
    host_url: str = "http://localhost:5173",
    validity_days: int = 365
) -> Credential:
    """Issue verifiable student credential with RS256 minimal JWT and QR code."""
    admission = (
        db.query(Admission)
        .filter(Admission.id == admission_id, Admission.institution_id == institution_id)
        .first()
    )
    if not admission:
        raise ValueError("Admission record not found or does not belong to submitting institution")

    # Check existing valid credential
    existing = (
        db.query(Credential)
        .filter(Credential.admission_id == admission_id, Credential.status == "valid")
        .first()
    )
    if existing:
        return existing

    opaque_ref = generate_opaque_reference()
    now = datetime.utcnow()
    expires_at = now + timedelta(days=validity_days)

    # RS256 Private key signing
    private_key, _ = get_rsa_keypair()
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    minimal_claims = {
        "iss": "AICTE-APAAR-PORTAL",
        "sub": f"STU-{admission.student_id}",
        "credential_id": opaque_ref,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp())
    }

    signed_jwt = jwt.encode(minimal_claims, pem_private, algorithm="RS256")

    # Generate QR Code: encodes ONLY https://<host>/verify/<opaque-ref>
    # NO APAAR ID, DOB, or personal student data in the QR!
    verify_url = f"{host_url.rstrip('/')}/verify/{opaque_ref}"
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    qr_data_uri = f"data:image/png;base64,{qr_base64}"

    credential = Credential(
        institution_id=institution_id,
        student_id=admission.student_id,
        admission_id=admission.id,
        opaque_reference=opaque_ref,
        credential_type="Enrolment Certificate",
        status="valid",
        jwt_token=signed_jwt,
        qr_data=qr_data_uri,
        issued_at=now,
        expires_at=expires_at
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return credential


def verify_credential_by_reference(
    db: Session,
    opaque_reference: str
) -> Dict[str, Any]:
    """Public credential verification by opaque reference.
    Returns ONLY: issuing institution, credential type, status (valid/revoked/expired/not_found).
    NO personal student details returned.
    """
    clean_ref = str(opaque_reference or "").strip()
    cred = db.query(Credential).filter(Credential.opaque_reference == clean_ref).first()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if not cred:
        return {
            "issuing_institution": "Unknown / Unregistered",
            "credential_type": "Student Credential",
            "status": "not_found",
            "issued_at": None,
            "verified_at": now_str
        }

    # Check expiration
    status_val = cred.status
    if status_val == "valid" and cred.expires_at and cred.expires_at < datetime.utcnow():
        status_val = "expired"

    inst_name = cred.institution.name if cred.institution else "Affiliated Technical Institution"

    return {
        "issuing_institution": inst_name,
        "credential_type": cred.credential_type,
        "status": status_val,
        "issued_at": cred.issued_at.strftime("%Y-%m-%d") if cred.issued_at else None,
        "verified_at": now_str
    }
