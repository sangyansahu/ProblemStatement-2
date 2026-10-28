import io
import os
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    UploadBatch, UploadRowResult, Programme, Student,
    Admission, ValidationCase, Institution
)
from app.security import (
    generate_apaar_token, mask_apaar_token, log_audit
)
from app.services.student_validator import (
    validate_missing_apaar, validate_demo_identifier, validate_seat_category,
    validate_academic_year, validate_admission_date
)
from app.services.duplicate_detector import (
    detect_duplicate_in_upload, detect_cross_institution_active_conflict,
    detect_duplicate_by_same_institution, detect_duplicate_student_number
)
from app.services.intake_validator import (
    calculate_excess, validate_intake_exceeded, validate_enrolment_growth_anomaly
)
from app.services.apaar_provider import MockApaarProvider

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ROW_COUNT = 5000

REQUIRED_COLUMNS = {"student_number", "apaar_id", "course_code", "academic_year", "seat_category"}
OPTIONAL_COLUMNS = {"name", "admission_date", "student_name"}
ALLOWED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def verify_file_magic_signature(content: bytes, filename: str) -> bool:
    """Validate extension and magic byte signature."""
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        # CSV text file check (not binary exe, zip, elf)
        if content.startswith(b"\x7fELF") or content.startswith(b"MZ"):
            return False
        return True
    elif lower_name.endswith(".xlsx"):
        # Zip container magic bytes (PK\x03\x04)
        return content.startswith(b"PK\x03\x04")
    return False


def process_student_upload(
    db: Session,
    institution_id: uuid.UUID,
    file_content: bytes,
    file_name: str,
    academic_year: str,
    uploaded_by: str
) -> Tuple[UploadBatch, List[UploadRowResult]]:
    """Process student CSV/XLSX file synchronously according to the strict 8-step pipeline."""
    # Step 1: File size and magic byte check
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum allowed size of 10 MB (received {len(file_content) / (1024*1024):.2f} MB)")

    if not verify_file_magic_signature(file_content, file_name):
        raise ValueError("Invalid file signature or unsupported format. Only standard CSV and XLSX are accepted.")

    # Step 2: SHA-256 Checksum and Idempotency
    checksum = hashlib.sha256(file_content).hexdigest()
    existing_batch = (
        db.query(UploadBatch)
        .filter(
            UploadBatch.institution_id == institution_id,
            UploadBatch.file_checksum == checksum,
            UploadBatch.status == "completed"
        )
        .first()
    )
    if existing_batch:
        # Idempotent return without duplicate admissions
        results = db.query(UploadRowResult).filter(UploadRowResult.batch_id == existing_batch.id).all()
        return existing_batch, results

    # Create new UploadBatch
    batch = UploadBatch(
        institution_id=institution_id,
        academic_year=academic_year,
        file_name=file_name,
        file_checksum=checksum,
        status="validating",
        uploaded_by=uploaded_by,
        created_at=datetime.utcnow()
    )
    db.add(batch)
    db.flush()

    # Step 3: Parse with pandas (dtype=str, keep_default_na=False)
    lower_name = file_name.lower()
    try:
        if lower_name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content), dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(io.BytesIO(file_content), dtype=str, keep_default_na=False)
    except Exception as e:
        batch.status = "failed"
        db.commit()
        raise ValueError(f"Failed to parse tabular file: {str(e)}")

    # Clean headers
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    # Normalize student_name -> name if provided
    if "student_name" in df.columns and "name" not in df.columns:
        df["name"] = df["student_name"]

    # Verify required columns allowlist
    missing_required = REQUIRED_COLUMNS - set(df.columns)
    if missing_required:
        batch.status = "failed"
        db.commit()
        raise ValueError(f"Missing mandatory columns: {', '.join(sorted(missing_required))}")

    # Row count limit check
    if len(df) > MAX_ROW_COUNT:
        batch.status = "failed"
        db.commit()
        raise ValueError(f"Row count ({len(df)}) exceeds maximum permitted per batch ({MAX_ROW_COUNT})")

    # Step 4, 5, 6: Row-level validation and conflict detection
    seen_in_upload: Set[str] = set()
    apaar_provider = MockApaarProvider()

    row_results: List[UploadRowResult] = []
    valid_admissions_to_commit: List[Dict[str, Any]] = []
    cases_to_create: List[ValidationCase] = []

    programmes_cache: Dict[str, Optional[Programme]] = {}

    for idx, row in df.iterrows():
        row_num = int(idx) + 1
        student_num = str(row.get("student_number", "")).strip()
        raw_apaar = str(row.get("apaar_id", "")).strip()
        course_code = str(row.get("course_code", "")).strip()
        row_year = str(row.get("academic_year", academic_year)).strip() or academic_year
        seat_cat = str(row.get("seat_category", "regular")).strip().lower()
        adm_date = str(row.get("admission_date", "")).strip() or None
        student_name = str(row.get("name", "")).strip() or None

        row_errors: List[Dict[str, Any]] = []
        row_warnings: List[Dict[str, Any]] = []

        # Rule: MISSING_APAAR
        err_missing = validate_missing_apaar(raw_apaar, row_num)
        if err_missing:
            row_errors.append(err_missing)

        # Rule: DEMO_IDENTIFIER_NOT_REAL
        if raw_apaar:
            warn_demo = validate_demo_identifier(raw_apaar, row_num)
            if warn_demo:
                row_warnings.append(warn_demo)

        # Rule: INVALID_SEAT_CATEGORY
        err_seat = validate_seat_category(seat_cat, row_num)
        if err_seat:
            row_errors.append(err_seat)

        # Rule: INVALID_ACADEMIC_YEAR
        err_year = validate_academic_year(row_year, row_num)
        if err_year:
            row_errors.append(err_year)

        # Rule: INVALID_ADMISSION_DATE
        if adm_date:
            err_date = validate_admission_date(adm_date, row_num)
            if err_date:
                row_errors.append(err_date)

        # Rule: DUPLICATE_IN_UPLOAD
        if raw_apaar:
            err_dup_upload = detect_duplicate_in_upload(seen_in_upload, raw_apaar, row_num)
            if err_dup_upload:
                row_errors.append(err_dup_upload)

        # Programme existence lookup (INVALID_COURSE_CODE)
        prog_cache_key = f"{course_code}_{row_year}"
        if prog_cache_key not in programmes_cache:
            prog = (
                db.query(Programme)
                .filter(
                    Programme.institution_id == institution_id,
                    Programme.course_code == course_code,
                    Programme.academic_year == row_year
                )
                .first()
            )
            programmes_cache[prog_cache_key] = prog
        programme = programmes_cache[prog_cache_key]

        if not programme:
            row_errors.append({
                "rule_code": "INVALID_COURSE_CODE",
                "severity": "error",
                "row_number": row_num,
                "message": f"Course code '{course_code}' is not registered under this institution for cycle '{row_year}'",
                "action": "reject_row",
                "requires_review": True
            })

        apaar_token = generate_apaar_token(raw_apaar) if raw_apaar else None
        masked_token = mask_apaar_token(apaar_token)

        # Duplicate & cross-institution checks if basic syntax passed
        if apaar_token and not row_errors:
            # Rule: CROSS_INSTITUTION_ACTIVE_CONFLICT
            conflict = detect_cross_institution_active_conflict(
                db, apaar_token, institution_id, row_year, row_num
            )
            if conflict:
                row_errors.append(conflict)
                cases_to_create.append(ValidationCase(
                    institution_id=institution_id,
                    programme_id=programme.id if programme else None,
                    student_id=conflict.get("conflicting_student_id"),
                    rule_code="CROSS_INSTITUTION_ACTIVE_CONFLICT",
                    severity="error",
                    academic_year=row_year,
                    message=conflict["message"],
                    status="open",
                    created_at=datetime.utcnow()
                ))

            # Rule: DUPLICATE_STUDENT_NUMBER
            if programme:
                dup_num = detect_duplicate_student_number(
                    db, programme.id, row_year, student_num, apaar_token, row_num
                )
                if dup_num:
                    row_errors.append(dup_num)

        # Mock APAAR Provider simulation check
        if raw_apaar and not row_errors:
            identity_res = apaar_provider.verify(raw_apaar)
            if identity_res.status == "unavailable":
                # Timeout simulated: flag for review, do not fail
                row_warnings.append({
                    "rule_code": "APAAR_SERVICE_UNAVAILABLE",
                    "severity": "notice",
                    "row_number": row_num,
                    "message": "Simulated identity authority timed out; marked pending external verification",
                    "action": "flag_notice",
                    "requires_review": True
                })

        # Compile row outcome
        if row_errors:
            primary_err = row_errors[0]
            row_res = UploadRowResult(
                batch_id=batch.id,
                row_number=row_num,
                student_number=student_num,
                apaar_token_masked=masked_token,
                rule_code=primary_err["rule_code"],
                severity=primary_err["severity"],
                status="rejected",
                message=primary_err["message"],
                action_taken=primary_err.get("action", "reject_row"),
                created_at=datetime.utcnow()
            )
            row_results.append(row_res)
        elif row_warnings:
            primary_warn = row_warnings[0]
            row_res = UploadRowResult(
                batch_id=batch.id,
                row_number=row_num,
                student_number=student_num,
                apaar_token_masked=masked_token,
                rule_code=primary_warn["rule_code"],
                severity=primary_warn["severity"],
                status="flagged",
                message=primary_warn["message"],
                action_taken=primary_warn.get("action", "flag_warning"),
                created_at=datetime.utcnow()
            )
            row_results.append(row_res)
            # Flagged warnings are also eligible to be admitted with pending review
            valid_admissions_to_commit.append({
                "row_number": row_num,
                "student_number": student_num,
                "apaar_token": apaar_token,
                "programme": programme,
                "academic_year": row_year,
                "seat_category": seat_cat,
                "admission_date": adm_date,
                "name": student_name,
                "status": "enrolled"
            })
        else:
            row_res = UploadRowResult(
                batch_id=batch.id,
                row_number=row_num,
                student_number=student_num,
                apaar_token_masked=masked_token,
                rule_code="PASSED",
                severity="accepted",
                status="accepted",
                message="Record passed verification checks",
                action_taken="accept_row",
                created_at=datetime.utcnow()
            )
            row_results.append(row_res)
            valid_admissions_to_commit.append({
                "row_number": row_num,
                "student_number": student_num,
                "apaar_token": apaar_token,
                "programme": programme,
                "academic_year": row_year,
                "seat_category": seat_cat,
                "admission_date": adm_date,
                "name": student_name,
                "status": "enrolled"
            })

    # Step 7: Commit valid records and validation cases in ONE transaction
    # Capacity check + admission write happens inside with row locking
    batch.total_rows = len(df)
    batch.accepted_rows = sum(1 for r in row_results if r.status == "accepted")
    batch.rejected_rows = sum(1 for r in row_results if r.status == "rejected")
    batch.flagged_rows = sum(1 for r in row_results if r.status == "flagged")

    # Group valid admissions by programme to check capacity with row lock
    grouped_by_prog: Dict[uuid.UUID, List[Dict[str, Any]]] = {}
    for item in valid_admissions_to_commit:
        prog = item["programme"]
        if prog.id not in grouped_by_prog:
            grouped_by_prog[prog.id] = []
        grouped_by_prog[prog.id].append(item)

    # Atomic commit
    for prog_id, items in grouped_by_prog.items():
        # SELECT ... FOR UPDATE row locking on Programme
        try:
            locked_prog = (
                db.query(Programme)
                .filter(Programme.id == prog_id)
                .with_for_update()
                .one()
            )
        except Exception:
            # Fallback if dialect does not support with_for_update (e.g. basic SQLite)
            locked_prog = db.query(Programme).filter(Programme.id == prog_id).one()

        # Count current active/enrolled admissions
        current_active = (
            db.query(func.count(Admission.id))
            .filter(
                Admission.programme_id == locked_prog.id,
                Admission.academic_year == locked_prog.academic_year,
                Admission.status.in_(["enrolled", "active"])
            )
            .scalar() or 0
        )

        projected_total = current_active + len(items)
        excess = calculate_excess(projected_total, locked_prog.approved_intake, locked_prog.approved_extra_seats)

        if excess > 0:
            # Raise INTAKE_EXCEEDED validation case for the institution
            intake_case = ValidationCase(
                institution_id=institution_id,
                programme_id=locked_prog.id,
                rule_code="INTAKE_EXCEEDED",
                severity="error",
                academic_year=locked_prog.academic_year,
                message=(
                    f"Programme {locked_prog.course_code} active enrolment ({projected_total}) "
                    f"exceeds ceiling ({locked_prog.approved_intake + locked_prog.approved_extra_seats}) by {excess} seats"
                ),
                status="open",
                created_at=datetime.utcnow()
            )
            cases_to_create.append(intake_case)

        # Write or update admissions
        for entry in items:
            # Check or create Student
            student = db.query(Student).filter(Student.apaar_id_token == entry["apaar_token"]).first()
            if not student:
                student = Student(
                    apaar_id_token=entry["apaar_token"],
                    name=entry["name"],
                    created_at=datetime.utcnow()
                )
                db.add(student)
                db.flush()

            # Check DUPLICATE_BY_SAME_INSTITUTION (idempotent handling)
            existing_adm = detect_duplicate_by_same_institution(
                db,
                entry["apaar_token"],
                institution_id,
                locked_prog.id,
                entry["academic_year"],
                entry["student_number"]
            )
            if existing_adm:
                # Idempotent update: update attributes if changed, do not duplicate
                existing_adm.seat_category = entry["seat_category"]
                if entry["admission_date"]:
                    existing_adm.admission_date = entry["admission_date"]
                existing_adm.updated_at = datetime.utcnow()
            else:
                new_adm = Admission(
                    student_id=student.id,
                    programme_id=locked_prog.id,
                    institution_id=institution_id,
                    student_number=entry["student_number"],
                    academic_year=entry["academic_year"],
                    seat_category=entry["seat_category"],
                    admission_date=entry["admission_date"],
                    status=entry["status"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_adm)

    # Persist row results, cases, and batch completion in single transaction
    for r in row_results:
        db.add(r)
    for c in cases_to_create:
        db.add(c)

    batch.status = "completed"
    batch.completed_at = datetime.utcnow()
    db.commit()

    # Step 8: Log audit entry
    log_audit(
        db=db,
        actor_id=uploaded_by,
        actor_role="institution_operator",
        institution_id=institution_id,
        action="upload_processed",
        target_reference=f"BATCH-{batch.id}",
        outcome="success",
        details=f"File {file_name}: total {batch.total_rows}, accepted {batch.accepted_rows}, rejected {batch.rejected_rows}, flagged {batch.flagged_rows}"
    )

    return batch, row_results
