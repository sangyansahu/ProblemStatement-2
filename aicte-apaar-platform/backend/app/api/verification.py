import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Credential, Admission, AuditLog
from app.schemas import (
    VerificationRequestCreate, CredentialResponse, PublicVerifyResult,
    AuditLogResponse
)
from app.security import (
    require_role, AuthenticatedUser, check_institution_access, log_audit
)
from app.services.credential_service import (
    issue_student_credential, verify_credential_by_reference
)

router = APIRouter(tags=["Credential Verification & Audit"])


@router.post("/verification-requests", response_model=CredentialResponse)
def create_verification_request(
    request: VerificationRequestCreate,
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "institution_operator", "verifier")
    ),
    db: Session = Depends(get_db)
):
    """Issue a verifiable credential for an admitted student.
    Generates opaque reference, RS256 JWT, and privacy-preserving QR code.
    """
    admission = db.query(Admission).filter(Admission.id == request.admission_id).first()
    if not admission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission record not found")

    check_institution_access(current_user, admission.institution_id)

    try:
        cred = issue_student_credential(
            db=db,
            admission_id=admission.id,
            institution_id=admission.institution_id
        )

        log_audit(
            db=db,
            actor_id=current_user.username,
            actor_role=current_user.role,
            institution_id=admission.institution_id,
            action="verification_access",
            target_reference=f"CREDENTIAL-{cred.opaque_reference}",
            outcome="success",
            details="Issued credential certificate with QR"
        )

        return CredentialResponse.model_validate(cred)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/credentials/{ref}/verify", response_model=PublicVerifyResult)
def public_verify_credential(
    ref: str,
    db: Session = Depends(get_db)
):
    """Public credential verification endpoint.
    Returns ONLY issuing institution, credential type, and status.
    NO personal student details, APAAR IDs, or DOBs are returned.
    """
    result = verify_credential_by_reference(db, ref)

    # Log public verification attempt
    log_audit(
        db=db,
        actor_id="anonymous_verifier",
        actor_role="public",
        action="verification_access",
        target_reference=f"CREDENTIAL-{ref}",
        outcome=result["status"],
        details=f"Public verification result: {result['status']}"
    )

    return PublicVerifyResult(**result)


@router.post("/credentials/{id}/revoke", response_model=CredentialResponse)
def revoke_credential(
    id: uuid.UUID,
    reason: str = Query("Administrative revocation"),
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "aicte_admin")
    ),
    db: Session = Depends(get_db)
):
    """Revoke an active credential."""
    cred = db.query(Credential).filter(Credential.id == id).first()
    if not cred:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    check_institution_access(current_user, cred.institution_id)

    cred.status = "revoked"
    cred.revoked_at = datetime.utcnow()
    cred.revocation_reason = reason.strip()

    db.commit()
    db.refresh(cred)

    log_audit(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        institution_id=cred.institution_id,
        action="verification_access",
        target_reference=f"CREDENTIAL-{cred.opaque_reference}",
        outcome="revoked",
        details=f"Credential revoked: {reason}"
    )

    return CredentialResponse.model_validate(cred)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(100, le=500),
    current_user: AuthenticatedUser = Depends(
        require_role("auditor", "aicte_admin")
    ),
    db: Session = Depends(get_db)
):
    """Read-only audit log inspection for auditor and aicte_admin roles."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [AuditLogResponse.model_validate(l) for l in logs]
