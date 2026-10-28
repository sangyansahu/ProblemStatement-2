import io
import csv
import re
import json
import uuid
from datetime import datetime
import pandas as pd
from app.extensions import db
from app.models.student import Student
from app.models.programme import Programme
from app.models.upload import UploadBatch
from app.models.duplicate_case import DuplicateReviewCase
from app.models.notification import Notification
from app.services.security_service import (
    validate_apaar_format,
    generate_apaar_hmac,
    mask_apaar,
    encrypt_apaar
)

EXPECTED_HEADERS = [
    'student_id',
    'apaar_id',
    'student_name',
    'programme_name',
    'branch_or_department',
    'academic_year',
    'admission_date',
    'enrolment_status',
    'admission_category',
    'supernumerary_status'
]

VALID_ENROLMENT_STATUSES = {'Active', 'Completed', 'Dropped Out', 'Suspended', 'Transferred'}
VALID_CATEGORIES = {'General', 'OBC', 'SC', 'ST', 'EWS', 'Management', 'NRI'}

def get_csv_template_content() -> str:
    """Returns sample CSV template with standard AICTE APAAR headers and sample rows."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(EXPECTED_HEADERS)
    writer.writerow([
        'STU-2025-001',
        '123456789012',
        'Aarav Sharma',
        'Bachelor of Technology',
        'Computer Science & Engineering',
        '2025-2026',
        '2025-08-01',
        'Active',
        'General',
        'No'
    ])
    writer.writerow([
        'STU-2025-002',
        '987654321098',
        'Priya Patel',
        'Bachelor of Technology',
        'Electronics & Communication Engineering',
        '2025-2026',
        '2025-08-01',
        'Active',
        'OBC',
        'No'
    ])
    writer.writerow([
        'STU-2025-003',
        '456789012345',
        'Rohan Verma',
        'Master of Technology',
        'Mechanical Engineering',
        '2025-2026',
        '2025-08-15',
        'Active',
        'EWS',
        'Yes'
    ])
    return output.getvalue()

def parse_and_validate_csv(file_bytes: bytes, institution_id: int):
    """
    Parses and validates CSV content line by line without committing to DB.
    Returns preview summary, header status, row validation list, and duplicate flags.
    """
    try:
        # Decode utf-8 or utf-8-sig (handles BOM)
        text = file_bytes.decode('utf-8-sig', errors='replace')
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to decode file encoding: {str(e)}'
        }

    f = io.StringIO(text)
    reader = csv.reader(f)
    try:
        headers = next(reader)
    except StopIteration:
        return {
            'success': False,
            'error': 'Uploaded CSV file is completely empty.'
        }

    # Normalize headers
    normalized_headers = [h.strip().lower().replace(' ', '_') for h in headers]
    missing_required = [h for h in EXPECTED_HEADERS if h not in normalized_headers]

    if missing_required:
        return {
            'success': False,
            'header_validation': False,
            'missing_headers': missing_required,
            'detected_headers': normalized_headers,
            'error': f"Missing required CSV column headers: {', '.join(missing_required)}"
        }

    # Pre-fetch existing data for this institution to detect collisions
    existing_students = Student.query.filter_by(institution_id=institution_id).all()
    existing_student_ids = {s.student_id: s for s in existing_students}

    # Pre-fetch all students across system for cross-institution APAAR HMAC collision checks
    all_students_hmac = {s.apaar_id_hmac: s for s in Student.query.filter(Student.apaar_id_hmac.isnot(None)).all()}

    file_student_ids = set()
    file_apaar_hmacs = set()

    row_results = []
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    duplicate_count = 0

    row_index = 1
    for raw_row in reader:
        row_index += 1
        if not raw_row or all(c.strip() == '' for c in raw_row):
            continue # Skip blank rows

        row_dict = dict(zip(normalized_headers, [c.strip() for c in raw_row]))
        
        errors = []
        warnings = []
        row_status = 'valid'

        student_id = row_dict.get('student_id', '')
        apaar_id = row_dict.get('apaar_id', '')
        student_name = row_dict.get('student_name', '')
        programme_name = row_dict.get('programme_name', '')
        branch = row_dict.get('branch_or_department', '')
        academic_year = row_dict.get('academic_year', '')
        admission_date = row_dict.get('admission_date', '')
        enrolment_status = row_dict.get('enrolment_status', 'Active')
        admission_category = row_dict.get('admission_category', 'General')
        supernumerary = str(row_dict.get('supernumerary_status', 'No')).strip().lower() in ['yes', 'true', '1']

        # 1. Check student_id
        if not student_id:
            errors.append({'field': 'student_id', 'message': 'Student ID is mandatory', 'suggestion': 'Provide a unique institutional student identifier'})
        elif student_id in file_student_ids:
            errors.append({'field': 'student_id', 'message': f"Duplicate Student ID '{student_id}' repeated within this CSV file", 'suggestion': 'Ensure each row has a distinct student ID'})
            duplicate_count += 1
        elif student_id in existing_student_ids:
            errors.append({'field': 'student_id', 'message': f"Student ID '{student_id}' already exists in your institution database", 'suggestion': 'Use record update workflow or verify roll number'})
            duplicate_count += 1
        else:
            file_student_ids.add(student_id)

        # 2. Check student_name
        if not student_name:
            errors.append({'field': 'student_name', 'message': 'Student Name is required', 'suggestion': 'Provide student full name as per official records'})
        elif len(student_name) < 2:
            warnings.append({'field': 'student_name', 'message': 'Student name seems unusually short', 'suggestion': 'Verify full name'})

        # 3. Check APAAR ID format & collisions
        is_apaar_valid = False
        apaar_hmac = None
        masked_apaar = mask_apaar(apaar_id)
        if apaar_id:
            valid_format, cleaned_or_err = validate_apaar_format(apaar_id)
            if not valid_format:
                errors.append({'field': 'apaar_id', 'message': cleaned_or_err, 'suggestion': 'APAAR ID must be 12 digits (e.g. 123456789012)'})
            else:
                is_apaar_valid = True
                apaar_hmac = generate_apaar_hmac(cleaned_or_err)
                if apaar_hmac in file_apaar_hmacs:
                    errors.append({'field': 'apaar_id', 'message': 'APAAR identifier repeated multiple times in this file', 'suggestion': 'Each student must have a distinct APAAR ID'})
                    duplicate_count += 1
                elif apaar_hmac in all_students_hmac:
                    conflict_student = all_students_hmac[apaar_hmac]
                    if conflict_student.institution_id != institution_id:
                        warnings.append({
                            'field': 'apaar_id',
                            'message': f"Potential cross-institution conflict: APAAR matches a student at {conflict_student.institution.name if conflict_student.institution else 'another institution'}. Will create a duplicate review case.",
                            'suggestion': 'Verify if student transferred or re-enrolled'
                        })
                        duplicate_count += 1
                    else:
                        errors.append({'field': 'apaar_id', 'message': f"APAAR ID already registered to student '{conflict_student.student_id}' in your institution", 'suggestion': 'Review existing student records'})
                        duplicate_count += 1
                file_apaar_hmacs.add(apaar_hmac)
        else:
            warnings.append({'field': 'apaar_id', 'message': 'APAAR ID is empty. Record will be stored as Not Submitted verification status.', 'suggestion': 'Assign APAAR ID when available'})

        # 4. Check programme and branch
        if not programme_name:
            errors.append({'field': 'programme_name', 'message': 'Programme Name is mandatory', 'suggestion': 'e.g. Bachelor of Technology'})
        if not branch:
            errors.append({'field': 'branch_or_department', 'message': 'Branch or Department is mandatory', 'suggestion': 'e.g. Computer Science & Engineering'})

        # 5. Check academic_year format
        if not academic_year:
            errors.append({'field': 'academic_year', 'message': 'Academic Year is required', 'suggestion': 'Use YYYY-YYYY format (e.g. 2025-2026)'})
        elif not re.match(r'^\d{4}-\d{4}$', academic_year):
            warnings.append({'field': 'academic_year', 'message': f"Academic year format '{academic_year}' should ideally be YYYY-YYYY", 'suggestion': 'e.g. 2025-2026'})

        # 6. Check admission date format
        if admission_date:
            try:
                datetime.strptime(admission_date, '%Y-%m-%d')
            except ValueError:
                warnings.append({'field': 'admission_date', 'message': f"Date format '{admission_date}' is not standard YYYY-MM-DD", 'suggestion': 'Format as YYYY-MM-DD'})

        # 7. Check enrolment status
        if enrolment_status and enrolment_status not in VALID_ENROLMENT_STATUSES:
            warnings.append({'field': 'enrolment_status', 'message': f"Non-standard enrolment status '{enrolment_status}'", 'suggestion': f"Allowed: {', '.join(VALID_ENROLMENT_STATUSES)}"})

        # Determine row status
        if errors:
            row_status = 'invalid'
            invalid_count += 1
        elif warnings:
            row_status = 'warning'
            warning_count += 1
            valid_count += 1 # warnings are still importable
        else:
            row_status = 'valid'
            valid_count += 1

        row_results.append({
            'row_number': row_index,
            'student_id': student_id or f"Row-{row_index}",
            'student_name': student_name,
            'apaar_id_masked': masked_apaar,
            'programme_name': programme_name,
            'branch_or_department': branch,
            'academic_year': academic_year,
            'admission_date': admission_date,
            'enrolment_status': enrolment_status,
            'admission_category': admission_category,
            'supernumerary_status': supernumerary,
            'raw_apaar': cleaned_or_err if is_apaar_valid else '',
            'apaar_hmac': apaar_hmac,
            'status': row_status,
            'errors': errors,
            'warnings': warnings
        })

    total_rows = len(row_results)

    return {
        'success': True,
        'header_validation': True,
        'detected_headers': normalized_headers,
        'total_rows': total_rows,
        'valid_rows': valid_count,
        'invalid_rows': invalid_count,
        'warning_rows': warning_count,
        'duplicate_candidates': duplicate_count,
        'row_results': row_results,
        'sample_preview': row_results[:10] # first 10 rows for instant preview table
    }

def commit_csv_import(institution_id: int, user_id: int, file_name: str, file_size: int, row_results: list):
    """
    Commits valid rows from the preview validation results into database inside a single atomic transaction.
    Creates UploadBatch record and DuplicateReviewCases for any cross-institution duplicates.
    """
    batch_reference = f"UB-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
    
    batch = UploadBatch(
        batch_id=batch_reference,
        institution_id=institution_id,
        file_name=file_name,
        file_size_bytes=file_size,
        total_rows=len(row_results),
        valid_rows=0,
        invalid_rows=0,
        warning_rows=0,
        duplicate_rows=0,
        status='processing',
        created_by_user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(batch)
    db.session.flush()

    committed_students = []
    error_report = []
    
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    duplicate_count = 0

    for row in row_results:
        if row.get('status') == 'invalid':
            invalid_count += 1
            error_report.append({
                'row_number': row.get('row_number'),
                'student_id': row.get('student_id'),
                'field': row.get('errors')[0]['field'] if row.get('errors') else 'unknown',
                'error': row.get('errors')[0]['message'] if row.get('errors') else 'Invalid data',
                'suggestion': row.get('errors')[0]['suggestion'] if row.get('errors') else ''
            })
            continue

        if row.get('status') == 'warning':
            warning_count += 1

        raw_apaar = row.get('raw_apaar')
        apaar_hmac = row.get('apaar_hmac')
        apaar_encrypted = encrypt_apaar(raw_apaar) if raw_apaar else None
        masked_apaar = mask_apaar(raw_apaar) if raw_apaar else 'Not Assigned'
        verification_status = 'pending' if raw_apaar else 'not_submitted'

        # Check for cross-institution duplicate conflict
        has_duplicate_conflict = False
        if apaar_hmac:
            conflict = Student.query.filter(
                Student.apaar_id_hmac == apaar_hmac,
                Student.institution_id != institution_id
            ).first()
            if conflict:
                has_duplicate_conflict = True
                duplicate_count += 1
                # Create DuplicateReviewCase
                dup_case = DuplicateReviewCase(
                    case_reference=f"DUP-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}",
                    issue_type='apaar_cross_institution',
                    severity='caution',
                    status='open',
                    institution_id=institution_id,
                    secondary_institution_id=conflict.institution_id,
                    student_id=row.get('student_id'),
                    student_name=row.get('student_name'),
                    apaar_id_masked=masked_apaar,
                    description=f"APAAR identifier matches existing student '{conflict.student_id}' enrolled at {conflict.institution.name if conflict.institution else 'secondary institution'}.",
                    details_json=json.dumps({
                        'import_student_id': row.get('student_id'),
                        'import_student_name': row.get('student_name'),
                        'import_programme': row.get('programme_name'),
                        'conflict_student_id': conflict.student_id,
                        'conflict_student_name': conflict.student_name,
                        'conflict_institution': conflict.institution.name if conflict.institution else 'Unknown'
                    }),
                    detected_at=datetime.utcnow()
                )
                db.session.add(dup_case)

        # Match or create Programme entry if needed
        programme = Programme.query.filter_by(
            institution_id=institution_id,
            programme_name=row.get('programme_name'),
            branch_or_department=row.get('branch_or_department')
        ).first()

        new_student = Student(
            institution_id=institution_id,
            student_id=row.get('student_id'),
            apaar_id_encrypted=apaar_encrypted,
            apaar_id_hmac=apaar_hmac,
            apaar_id_masked=masked_apaar,
            student_name=row.get('student_name'),
            programme_id=programme.id if programme else None,
            programme_name=row.get('programme_name'),
            branch_or_department=row.get('branch_or_department'),
            academic_year=row.get('academic_year') or '2025-2026',
            admission_date=row.get('admission_date') or datetime.utcnow().strftime('%Y-%m-%d'),
            enrolment_status=row.get('enrolment_status') or 'Active',
            admission_category=row.get('admission_category') or 'General',
            supernumerary_status=row.get('supernumerary_status', False),
            verification_status=verification_status,
            verification_source='simulated',
            is_duplicate_flagged=has_duplicate_conflict,
            upload_batch_id=batch.id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_student)
        committed_students.append(new_student)
        valid_count += 1

    # Update batch status
    batch.valid_rows = valid_count
    batch.invalid_rows = invalid_count
    batch.warning_rows = warning_count
    batch.duplicate_rows = duplicate_count
    batch.error_report_json = json.dumps(error_report) if error_report else None
    batch.status = 'completed'
    batch.completed_at = datetime.utcnow()

    # Generate Notification for institution
    notif = Notification(
        institution_id=institution_id,
        role_target='institute',
        title=f"CSV Import Completed ({batch_reference})",
        message=f"Successfully imported {valid_count} student records. {invalid_count} rejected, {duplicate_count} duplicate cases flagged.",
        link=f"/uploads",
        type='success' if invalid_count == 0 else 'warning'
    )
    db.session.add(notif)

    db.session.commit()

    return {
        'batch_id': batch.batch_id,
        'total_processed': len(row_results),
        'imported_count': valid_count,
        'rejected_count': invalid_count,
        'warning_count': warning_count,
        'duplicate_candidates': duplicate_count,
        'completed_at': batch.completed_at.isoformat()
    }
