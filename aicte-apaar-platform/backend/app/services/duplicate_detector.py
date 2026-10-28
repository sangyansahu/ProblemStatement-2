import uuid
from typing import Dict, Any, Optional, List, Set
from sqlalchemy.orm import Session
from app.models import Student, Admission, Programme


def detect_duplicate_in_upload(
    seen_identifiers: Set[str],
    apaar_id: str,
    row_number: int = 0
) -> Optional[Dict[str, Any]]:
    """DUPLICATE_IN_UPLOAD rule: same identifier repeated in one file."""
    norm = str(apaar_id or "").strip().upper()
    if not norm:
        return None

    if norm in seen_identifiers:
        return {
            "rule_code": "DUPLICATE_IN_UPLOAD",
            "severity": "error",
            "row_number": row_number,
            "message": "Duplicate candidate: identifier repeated within the same upload batch",
            "action": "reject_row",
            "requires_review": True
        }
    seen_identifiers.add(norm)
    return None


def detect_cross_institution_active_conflict(
    db: Session,
    apaar_token: str,
    current_institution_id: uuid.UUID,
    academic_year: str,
    row_number: int = 0
) -> Optional[Dict[str, Any]]:
    """CROSS_INSTITUTION_ACTIVE_CONFLICT rule:
    Same canonical student with active admissions at >1 institution;
    raises a case for review, never auto-deletes or auto-merges.
    """
    existing_student = db.query(Student).filter(Student.apaar_id_token == apaar_token).first()
    if not existing_student:
        return None

    active_admissions = (
        db.query(Admission)
        .filter(
            Admission.student_id == existing_student.id,
            Admission.institution_id != current_institution_id,
            Admission.academic_year == academic_year,
            Admission.status.in_(["enrolled", "active"])
        )
        .all()
    )

    if active_admissions:
        other_inst_codes = [str(adm.institution_id) for adm in active_admissions]
        return {
            "rule_code": "CROSS_INSTITUTION_ACTIVE_CONFLICT",
            "severity": "error",
            "row_number": row_number,
            "message": (
                f"Potential duplicate conflict: student holds active enrolment at another institution "
                f"during academic cycle {academic_year}"
            ),
            "action": "flag_case",
            "requires_review": True,
            "conflicting_student_id": existing_student.id
        }
    return None


def detect_duplicate_by_same_institution(
    db: Session,
    apaar_token: str,
    institution_id: uuid.UUID,
    programme_id: uuid.UUID,
    academic_year: str,
    student_number: str
) -> Optional[Admission]:
    """DUPLICATE_BY_SAME_INSTITUTION:
    Database lookup; handled idempotently. If existing admission found for this programme, year, student_number.
    """
    existing_student = db.query(Student).filter(Student.apaar_id_token == apaar_token).first()
    if not existing_student:
        return None

    existing_adm = (
        db.query(Admission)
        .filter(
            Admission.student_id == existing_student.id,
            Admission.programme_id == programme_id,
            Admission.academic_year == academic_year,
            Admission.student_number == student_number
        )
        .first()
    )
    return existing_adm


def detect_duplicate_student_number(
    db: Session,
    programme_id: uuid.UUID,
    academic_year: str,
    student_number: str,
    current_apaar_token: str,
    row_number: int = 0
) -> Optional[Dict[str, Any]]:
    """DUPLICATE_STUDENT_NUMBER (unique per programme + academic year).
    Flag if student_number is assigned to a DIFFERENT student in that programme/year.
    """
    adm = (
        db.query(Admission)
        .join(Student, Admission.student_id == Student.id)
        .filter(
            Admission.programme_id == programme_id,
            Admission.academic_year == academic_year,
            Admission.student_number == student_number
        )
        .first()
    )
    if adm and adm.student and adm.student.apaar_id_token != current_apaar_token:
        return {
            "rule_code": "DUPLICATE_STUDENT_NUMBER",
            "severity": "error",
            "row_number": row_number,
            "message": f"Student number '{student_number}' is already allocated to another record in this programme",
            "action": "reject_row",
            "requires_review": True
        }
    return None
