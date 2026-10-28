import io
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import openpyxl
from app.database import get_db
from app.models import (
    Institution, Programme, Admission, Student,
    ValidationCase, UploadBatch
)
from app.schemas import (
    NationalAnalyticsResponse, InstitutionAnalyticsResponse,
    EnrolmentYearStat, ProgrammeResponse, ValidationCaseResponse
)
from app.security import (
    require_role, AuthenticatedUser, check_institution_access, log_audit, mask_apaar_token
)

router = APIRouter(tags=["Analytics & Reports"])


@router.get("/analytics/national", response_model=NationalAnalyticsResponse)
def get_national_analytics(
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """National AICTE analytics aggregating institutions, enrolments, and flags."""
    # 1. Institutions reporting (institutions with at least 1 completed upload batch or admission)
    inst_reporting_count = (
        db.query(func.count(distinct(Admission.institution_id)))
        .filter(Admission.status.in_(["enrolled", "active"]))
        .scalar() or 0
    )

    # 2. Total students reported (distinct canonical students)
    students_reported_count = (
        db.query(func.count(distinct(Admission.student_id)))
        .filter(Admission.status.in_(["enrolled", "active"]))
        .scalar() or 0
    )

    # 3. Records flagged (validation cases with warning or notice severity, or total flagged rows)
    records_flagged_count = (
        db.query(func.count(ValidationCase.id))
        .filter(ValidationCase.severity.in_(["warning", "notice"]))
        .scalar() or 0
    )

    # 4. Pending reviews (open validation cases)
    pending_reviews_count = (
        db.query(func.count(ValidationCase.id))
        .filter(ValidationCase.status == "open")
        .scalar() or 0
    )

    # Total approved intake ceiling
    total_approved = (
        db.query(func.sum(Programme.approved_intake + Programme.approved_extra_seats))
        .scalar() or 0
    )

    total_active_admissions = (
        db.query(func.count(Admission.id))
        .filter(Admission.status.in_(["enrolled", "active"]))
        .scalar() or 0
    )

    utilisation_pct = (total_active_admissions / total_approved * 100.0) if total_approved > 0 else 0.0

    # Enrolment by academic year for Recharts bar chart
    year_stats = (
        db.query(
            Admission.academic_year,
            func.count(Admission.id).label("count")
        )
        .filter(Admission.status.in_(["enrolled", "active"]))
        .group_by(Admission.academic_year)
        .order_by(Admission.academic_year.asc())
        .all()
    )

    enrolment_chart_data = [
        EnrolmentYearStat(academic_year=row[0], enrolment_count=row[1])
        for row in year_stats
    ]
    if not enrolment_chart_data:
        enrolment_chart_data = [
            EnrolmentYearStat(academic_year="2024-25", enrolment_count=0),
            EnrolmentYearStat(academic_year="2025-26", enrolment_count=total_active_admissions)
        ]

    return NationalAnalyticsResponse(
        institutions_reporting=inst_reporting_count,
        students_reported=students_reported_count,
        records_flagged=records_flagged_count,
        pending_reviews=pending_reviews_count,
        total_approved_intake=int(total_approved),
        overall_utilisation_pct=round(utilisation_pct, 1),
        enrolment_by_year=enrolment_chart_data
    )


@router.get("/analytics/institution", response_model=InstitutionAnalyticsResponse)
def get_institution_analytics(
    institution_id: Optional[uuid.UUID] = Query(None),
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "institution_operator", "aicte_admin", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Institutional analytics: total enrolment, approved capacity, utilisation %, pending cases."""
    target_id = institution_id
    if not (current_user.is_aicte_admin or current_user.is_auditor):
        target_id = current_user.institution_id

    if not target_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution ID required")

    check_institution_access(current_user, target_id)

    institution = db.query(Institution).filter(Institution.id == target_id).first()
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    # Total active enrolment
    total_enrolment = (
        db.query(func.count(Admission.id))
        .filter(
            Admission.institution_id == target_id,
            Admission.status.in_(["enrolled", "active"])
        )
        .scalar() or 0
    )

    # Approved intake
    total_intake = (
        db.query(func.sum(Programme.approved_intake + Programme.approved_extra_seats))
        .filter(Programme.institution_id == target_id)
        .scalar() or 0
    )

    utilisation = (total_enrolment / total_intake * 100.0) if total_intake > 0 else 0.0

    # Pending validation cases
    pending_cases = (
        db.query(func.count(ValidationCase.id))
        .filter(
            ValidationCase.institution_id == target_id,
            ValidationCase.status == "open"
        )
        .scalar() or 0
    )

    # Programmes detail
    programmes = (
        db.query(Programme)
        .filter(Programme.institution_id == target_id)
        .order_by(Programme.course_code.asc())
        .all()
    )
    prog_responses = []
    for p in programmes:
        enrolled = (
            db.query(func.count(Admission.id))
            .filter(
                Admission.programme_id == p.id,
                Admission.academic_year == p.academic_year,
                Admission.status.in_(["enrolled", "active"])
            )
            .scalar() or 0
        )
        cap = p.approved_intake + p.approved_extra_seats
        ut = (enrolled / cap * 100.0) if cap > 0 else 0.0
        prog_responses.append(ProgrammeResponse(
            id=p.id,
            institution_id=p.institution_id,
            course_code=p.course_code,
            programme_name=p.programme_name,
            academic_year=p.academic_year,
            approved_intake=p.approved_intake,
            approved_extra_seats=p.approved_extra_seats,
            enrolled_count=enrolled,
            utilisation_pct=round(ut, 1)
        ))

    return InstitutionAnalyticsResponse(
        institution_id=institution.id,
        institution_name=institution.name,
        total_reported_enrolment=total_enrolment,
        approved_intake=int(total_intake),
        capacity_utilisation_pct=round(utilisation, 1),
        pending_validation_cases=pending_cases,
        programmes=prog_responses
    )


@router.get("/reports/enrolment")
def export_enrolment_report(
    academic_year: Optional[str] = Query(None),
    institution_id: Optional[uuid.UUID] = Query(None),
    current_user: AuthenticatedUser = Depends(
        require_role("aicte_admin", "institution_admin", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Export enrolment report as standard XLSX workbook.
    Excludes raw APAAR IDs (only masked tokens exported).
    Writes an audit log entry.
    """
    target_id = institution_id
    if not (current_user.is_aicte_admin or current_user.is_auditor):
        target_id = current_user.institution_id

    if target_id:
        check_institution_access(current_user, target_id)

    query = (
        db.query(Admission)
        .join(Programme, Admission.programme_id == Programme.id)
        .join(Institution, Admission.institution_id == Institution.id)
        .join(Student, Admission.student_id == Student.id)
    )

    if target_id:
        query = query.filter(Admission.institution_id == target_id)

    if academic_year:
        query = query.filter(Admission.academic_year == academic_year.strip())

    admissions = query.order_by(Institution.name.asc(), Programme.course_code.asc()).all()

    # Generate XLSX with openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Enrolment Registry"

    headers = [
        "Institution AICTE Code", "Institution Name", "Course Code", "Programme Name",
        "Academic Cycle", "Student Number", "Student Name", "Masked APAAR Token",
        "Seat Category", "Admission Date", "Enrolment Status"
    ]
    ws.append(headers)

    for adm in admissions:
        ws.append([
            adm.institution.aicte_code if adm.institution else "",
            adm.institution.name if adm.institution else "",
            adm.programme.course_code if adm.programme else "",
            adm.programme.programme_name if adm.programme else "",
            adm.academic_year,
            adm.student_number,
            adm.student.name if adm.student else "—",
            mask_apaar_token(adm.student.apaar_id_token) if adm.student else "—",
            adm.seat_category,
            adm.admission_date or "—",
            adm.status
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Audit log entry for report export
    log_audit(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        institution_id=target_id,
        action="report_export",
        target_reference=f"ENROLMENT-REPORT-{academic_year or 'ALL'}",
        outcome="success",
        details=f"Exported {len(admissions)} enrolment rows to XLSX"
    )

    filename = f"aicte_enrolment_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
