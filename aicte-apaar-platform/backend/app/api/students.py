import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Student, Admission, Programme, Institution
from app.schemas import AdmissionResponse, StudentDetailResponse, StudentPatchRequest
from app.security import (
    require_role, AuthenticatedUser, mask_apaar_token,
    check_institution_access, log_audit
)
from app.services.student_validator import validate_status_transition, validate_seat_category

router = APIRouter(prefix="/students", tags=["Student Records"])


@router.get("", response_model=List[AdmissionResponse])
def list_students(
    academic_year: Optional[str] = Query(None, description="Filter by academic cycle (e.g. 2025-26)"),
    status: Optional[str] = Query(None, description="Filter by status (enrolled, active, withdrawn, cancelled)"),
    course_code: Optional[str] = Query(None, description="Filter by course code"),
    search: Optional[str] = Query(None, description="Search by student number or name"),
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """List student admissions.
    Query-level institution-scoped for institution roles.
    Verifier role is explicitly excluded and cannot read student profiles.
    """
    query = (
        db.query(Admission)
        .join(Programme, Admission.programme_id == Programme.id)
        .join(Institution, Admission.institution_id == Institution.id)
        .join(Student, Admission.student_id == Student.id)
    )

    # Institution scope filter
    if not (current_user.is_aicte_admin or current_user.is_auditor):
        if not current_user.institution_id:
            return []
        query = query.filter(Admission.institution_id == current_user.institution_id)

    if academic_year:
        query = query.filter(Admission.academic_year == academic_year.strip())

    if status:
        query = query.filter(Admission.status == status.strip().lower())

    if course_code:
        query = query.filter(Programme.course_code == course_code.strip())

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Admission.student_number.ilike(s)) | (Student.name.ilike(s))
        )

    admissions = query.order_by(Admission.created_at.desc()).limit(500).all()

    results = []
    for adm in admissions:
        results.append(AdmissionResponse(
            id=adm.id,
            student_id=adm.student_id,
            programme_id=adm.programme_id,
            institution_id=adm.institution_id,
            student_number=adm.student_number,
            academic_year=adm.academic_year,
            seat_category=adm.seat_category,
            admission_date=adm.admission_date,
            status=adm.status,
            course_code=adm.programme.course_code if adm.programme else None,
            programme_name=adm.programme.programme_name if adm.programme else None,
            institution_name=adm.institution.name if adm.institution else None,
            created_at=adm.created_at
        ))
    return results


@router.get("/{id}", response_model=StudentDetailResponse)
def get_student_detail(
    id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Get single student profile and historical admissions.
    Enforces institution scope.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student record not found")

    # Scope check: verify student has at least one admission accessible to this user
    accessible_admissions = []
    for adm in student.admissions:
        if current_user.is_aicte_admin or current_user.is_auditor:
            accessible_admissions.append(adm)
        elif current_user.institution_id and adm.institution_id == current_user.institution_id:
            accessible_admissions.append(adm)

    if not accessible_admissions and not (current_user.is_aicte_admin or current_user.is_auditor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: student has no admissions belonging to your institution"
        )

    admission_responses = [
        AdmissionResponse(
            id=adm.id,
            student_id=adm.student_id,
            programme_id=adm.programme_id,
            institution_id=adm.institution_id,
            student_number=adm.student_number,
            academic_year=adm.academic_year,
            seat_category=adm.seat_category,
            admission_date=adm.admission_date,
            status=adm.status,
            course_code=adm.programme.course_code if adm.programme else None,
            programme_name=adm.programme.programme_name if adm.programme else None,
            institution_name=adm.institution.name if adm.institution else None,
            created_at=adm.created_at
        )
        for adm in accessible_admissions
    ]

    return StudentDetailResponse(
        id=student.id,
        apaar_token_masked=mask_apaar_token(student.apaar_id_token),
        name=student.name,
        admissions=admission_responses,
        created_at=student.created_at
    )


@router.patch("/{id}", response_model=AdmissionResponse)
def patch_student_admission(
    id: uuid.UUID,
    patch_data: StudentPatchRequest,
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "institution_operator")
    ),
    db: Session = Depends(get_db)
):
    """PATCH permitted fields only (name, seat_category, status).
    Validates status transition and logs audit entry.
    """
    admission = db.query(Admission).filter(Admission.id == id).first()
    if not admission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission record not found")

    check_institution_access(current_user, admission.institution_id)

    changed_fields = []

    # Update Student Name if permitted
    if patch_data.name is not None and patch_data.name.strip():
        if admission.student:
            admission.student.name = patch_data.name.strip()
            changed_fields.append(f"name='{patch_data.name.strip()}'")

    # Update Seat Category if permitted
    if patch_data.seat_category is not None:
        val_cat = patch_data.seat_category.strip().lower()
        err_cat = validate_seat_category(val_cat)
        if err_cat:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_cat["message"])
        if admission.seat_category != val_cat:
            admission.seat_category = val_cat
            changed_fields.append(f"seat_category='{val_cat}'")

    # Update Status if permitted (enforces transition validity)
    if patch_data.status is not None:
        new_status = patch_data.status.strip().lower()
        err_trans = validate_status_transition(admission.status, new_status)
        if err_trans:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_trans["message"])
        if admission.status != new_status:
            old_status = admission.status
            admission.status = new_status
            changed_fields.append(f"status: '{old_status}' -> '{new_status}'")

    if changed_fields:
        db.commit()
        db.refresh(admission)

        log_audit(
            db=db,
            actor_id=current_user.username,
            actor_role=current_user.role,
            institution_id=admission.institution_id,
            action="record_updated",
            target_reference=f"ADMISSION-{admission.id}",
            outcome="success",
            details=f"Updated: {', '.join(changed_fields)}"
        )

    return AdmissionResponse(
        id=admission.id,
        student_id=admission.student_id,
        programme_id=admission.programme_id,
        institution_id=admission.institution_id,
        student_number=admission.student_number,
        academic_year=admission.academic_year,
        seat_category=admission.seat_category,
        admission_date=admission.admission_date,
        status=admission.status,
        course_code=admission.programme.course_code if admission.programme else None,
        programme_name=admission.programme.programme_name if admission.programme else None,
        institution_name=admission.institution.name if admission.institution else None,
        created_at=admission.created_at
    )
