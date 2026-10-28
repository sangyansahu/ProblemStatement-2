import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Institution, Programme, Admission
from app.schemas import InstitutionResponse, ProgrammeResponse
from app.security import (
    require_role, AuthenticatedUser, check_institution_access
)

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("", response_model=List[InstitutionResponse])
def list_institutions(
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """List affiliated institutions.
    aicte_admin and auditor see all institutions.
    Institution users see only their own affiliated institution.
    """
    if current_user.is_aicte_admin or current_user.is_auditor:
        institutions = db.query(Institution).order_by(Institution.name.asc()).all()
    else:
        if not current_user.institution_id:
            return []
        institutions = db.query(Institution).filter(Institution.id == current_user.institution_id).all()

    return [InstitutionResponse.model_validate(inst) for inst in institutions]


@router.get("/{id}", response_model=InstitutionResponse)
def get_institution(
    id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Get institution profile by ID."""
    check_institution_access(current_user, id)
    inst = db.query(Institution).filter(Institution.id == id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return InstitutionResponse.model_validate(inst)


@router.get("/{id}/programmes", response_model=List[ProgrammeResponse])
def get_institution_programmes(
    id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """List programmes for institution with reported enrolment and capacity utilisation %."""
    check_institution_access(current_user, id)

    programmes = (
        db.query(Programme)
        .filter(Programme.institution_id == id)
        .order_by(Programme.course_code.asc())
        .all()
    )

    results = []
    for prog in programmes:
        # Count active/enrolled admissions
        enrolled = (
            db.query(func.count(Admission.id))
            .filter(
                Admission.programme_id == prog.id,
                Admission.academic_year == prog.academic_year,
                Admission.status.in_(["enrolled", "active"])
            )
            .scalar() or 0
        )
        total_capacity = prog.approved_intake + prog.approved_extra_seats
        utilisation = (enrolled / total_capacity * 100.0) if total_capacity > 0 else 0.0

        results.append(ProgrammeResponse(
            id=prog.id,
            institution_id=prog.institution_id,
            course_code=prog.course_code,
            programme_name=prog.programme_name,
            academic_year=prog.academic_year,
            approved_intake=prog.approved_intake,
            approved_extra_seats=prog.approved_extra_seats,
            enrolled_count=enrolled,
            utilisation_pct=round(utilisation, 1)
        ))
    return results
