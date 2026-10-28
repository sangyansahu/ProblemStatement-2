import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ValidationCase, Institution, Programme
from app.schemas import ValidationCaseResponse, ResolveCaseRequest
from app.security import (
    require_role, AuthenticatedUser, check_institution_access, log_audit
)

router = APIRouter(prefix="/validation-cases", tags=["Validation Cases"])


@router.get("", response_model=List[ValidationCaseResponse])
def list_validation_cases(
    status_filter: Optional[str] = Query(None, alias="status"),
    rule_code: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """List validation cases with filters. Enforces institution scope."""
    query = (
        db.query(ValidationCase)
        .join(Institution, ValidationCase.institution_id == Institution.id)
        .outerjoin(Programme, ValidationCase.programme_id == Programme.id)
    )

    if not (current_user.is_aicte_admin or current_user.is_auditor):
        if not current_user.institution_id:
            return []
        query = query.filter(ValidationCase.institution_id == current_user.institution_id)

    if status_filter:
        query = query.filter(ValidationCase.status == status_filter.strip().lower())

    if rule_code:
        query = query.filter(ValidationCase.rule_code == rule_code.strip())

    if severity:
        query = query.filter(ValidationCase.severity == severity.strip().lower())

    if academic_year:
        query = query.filter(ValidationCase.academic_year == academic_year.strip())

    cases = query.order_by(ValidationCase.created_at.desc()).limit(200).all()

    results = []
    for c in cases:
        results.append(ValidationCaseResponse(
            id=c.id,
            institution_id=c.institution_id,
            institution_name=c.institution.name if c.institution else None,
            programme_id=c.programme_id,
            course_code=c.programme.course_code if c.programme else None,
            student_id=c.student_id,
            rule_code=c.rule_code,
            severity=c.severity,
            academic_year=c.academic_year,
            message=c.message,
            status=c.status,
            resolution_note=c.resolution_note,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at,
            created_at=c.created_at
        ))
    return results


@router.post("/{id}/resolve", response_model=ValidationCaseResponse)
def resolve_validation_case(
    id: uuid.UUID,
    resolve_data: ResolveCaseRequest,
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin")
    ),
    db: Session = Depends(get_db)
):
    """Resolve or dismiss a validation case with a required justification note.
    Historical validation cases are NEVER deleted; status changes only.
    Writes an audit log entry.
    """
    case = db.query(ValidationCase).filter(ValidationCase.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation case not found")

    check_institution_access(current_user, case.institution_id)

    if not resolve_data.resolution_note or len(resolve_data.resolution_note.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A substantive justification note is mandatory to resolve a validation case"
        )

    action_status = "dismissed" if resolve_data.action == "dismiss" else "resolved"
    case.status = action_status
    case.resolution_note = resolve_data.resolution_note.strip()
    case.resolved_by = current_user.username
    case.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(case)

    log_audit(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        institution_id=case.institution_id,
        action="validation_case_resolved",
        target_reference=f"CASE-{case.id}",
        outcome="success",
        details=f"Rule {case.rule_code} marked {action_status}. Note: {case.resolution_note}"
    )

    return ValidationCaseResponse(
        id=case.id,
        institution_id=case.institution_id,
        institution_name=case.institution.name if case.institution else None,
        programme_id=case.programme_id,
        course_code=case.programme.course_code if case.programme else None,
        student_id=case.student_id,
        rule_code=case.rule_code,
        severity=case.severity,
        academic_year=case.academic_year,
        message=case.message,
        status=case.status,
        resolution_note=case.resolution_note,
        resolved_by=case.resolved_by,
        resolved_at=case.resolved_at,
        created_at=case.created_at
    )
