import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.student import Student
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.change_history import RecordChangeHistory
from app.models.duplicate_case import DuplicateReviewCase
from app.models.audit import AuditLog
from app.services.security_service import (
    validate_apaar_format,
    generate_apaar_hmac,
    mask_apaar,
    encrypt_apaar
)
from app.utils.auth_helper import get_current_user, role_required

students_bp = Blueprint('students', __name__, url_prefix='/api/v1/students')

@students_bp.route('', methods=['GET'])
@jwt_required()
def list_students():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = Student.query

    # Enforce strict institution isolation for institute role
    if user.role == 'institute':
        if not user.institution_id:
            return jsonify({'students': [], 'total': 0, 'page': 1, 'pages': 1}), 200
        query = query.filter(Student.institution_id == user.institution_id)
    else:
        # Admin / Super Admin can filter by institution
        inst_id = request.args.get('institution_id', type=int)
        if inst_id:
            query = query.filter(Student.institution_id == inst_id)

    # Search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (Student.student_id.ilike(f"%{search}%")) |
            (Student.student_name.ilike(f"%{search}%")) |
            (Student.branch_or_department.ilike(f"%{search}%")) |
            (Student.programme_name.ilike(f"%{search}%"))
        )

    # Secondary filters
    prog = request.args.get('programme', '').strip()
    if prog:
        query = query.filter(Student.programme_name == prog)

    ay = request.args.get('academic_year', '').strip()
    if ay:
        query = query.filter(Student.academic_year == ay)

    vstatus = request.args.get('verification_status', '').strip()
    if vstatus:
        query = query.filter(Student.verification_status == vstatus)

    estatus = request.args.get('enrolment_status', '').strip()
    if estatus:
        query = query.filter(Student.enrolment_status == estatus)

    is_dup = request.args.get('is_duplicate_flagged')
    if is_dup is not None and is_dup != '':
        query = query.filter(Student.is_duplicate_flagged == (is_dup.lower() in ['true', '1']))

    # Sorting
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    sort_col = getattr(Student, sort_by, Student.created_at)
    if order == 'asc':
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    total = query.count()
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'students': [s.to_dict() for s in paginated.items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages
    }), 200

@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Strict isolation for Institute
    if user.role == 'institute' and student.institution_id != user.institution_id:
        return jsonify({'error': 'Forbidden', 'message': 'Access to students from other institutions is forbidden.'}), 403

    data = student.to_dict()
    # Include Change History and Duplicate Cases
    data['change_history'] = [ch.to_dict() for ch in student.change_history]
    
    # Related duplicate cases
    dup_cases = DuplicateReviewCase.query.filter(
        (DuplicateReviewCase.student_id == student.student_id) &
        ((DuplicateReviewCase.institution_id == student.institution_id) | (DuplicateReviewCase.secondary_institution_id == student.institution_id))
    ).all()
    data['related_duplicate_cases'] = [dc.to_dict() for dc in dup_cases]

    return jsonify({'student': data}), 200

@students_bp.route('', methods=['POST'])
@jwt_required()
def create_student():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}

    # Determine institution_id
    if user.role == 'institute':
        institution_id = user.institution_id
    else:
        institution_id = data.get('institution_id')
        if not institution_id:
            return jsonify({'error': 'institution_id is required for administrative creation'}), 400

    student_id = data.get('student_id', '').strip()
    student_name = data.get('student_name', '').strip()
    programme_name = data.get('programme_name', '').strip()
    branch = data.get('branch_or_department', '').strip()
    academic_year = data.get('academic_year', '2025-2026').strip()
    raw_apaar = data.get('apaar_id', '').strip()

    if not student_id or not student_name or not programme_name or not branch:
        return jsonify({'error': 'student_id, student_name, programme_name, and branch_or_department are required'}), 400

    # Check student_id collision within institution
    if Student.query.filter_by(institution_id=institution_id, student_id=student_id).first():
        return jsonify({'error': f"Student ID '{student_id}' already exists in this institution"}), 409

    # APAAR processing
    apaar_hmac = None
    apaar_encrypted = None
    masked_apaar = 'Not Assigned'
    verification_status = 'not_submitted'
    is_duplicate = False

    if raw_apaar:
        valid_format, cleaned_or_err = validate_apaar_format(raw_apaar)
        if not valid_format:
            return jsonify({'error': f"APAAR ID invalid: {cleaned_or_err}"}), 400
        apaar_hmac = generate_apaar_hmac(cleaned_or_err)
        apaar_encrypted = encrypt_apaar(cleaned_or_err)
        masked_apaar = mask_apaar(cleaned_or_err)
        verification_status = 'pending'

        # Check cross-institution conflict
        conflict = Student.query.filter(Student.apaar_id_hmac == apaar_hmac).first()
        if conflict:
            is_duplicate = True

    new_student = Student(
        institution_id=institution_id,
        student_id=student_id,
        apaar_id_encrypted=apaar_encrypted,
        apaar_id_hmac=apaar_hmac,
        apaar_id_masked=masked_apaar,
        student_name=student_name,
        programme_name=programme_name,
        branch_or_department=branch,
        academic_year=academic_year,
        admission_date=data.get('admission_date'),
        enrolment_status=data.get('enrolment_status', 'Active'),
        admission_category=data.get('admission_category', 'General'),
        supernumerary_status=data.get('supernumerary_status', False),
        verification_status=verification_status,
        verification_source='simulated',
        is_duplicate_flagged=is_duplicate,
        created_at=datetime.utcnow()
    )
    db.session.add(new_student)
    db.session.flush()

    # Track creation history
    history = RecordChangeHistory(
        student_id=new_student.id,
        changed_by_user_id=user.id,
        changed_by_name=user.full_name,
        change_type='creation',
        field_name='all',
        new_value=f"Created student {student_name} ({student_id})",
        reason=data.get('reason', 'Initial record entry'),
        timestamp=datetime.utcnow()
    )
    db.session.add(history)

    # Audit log
    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='STUDENT_RECORD_CREATED',
        target_type='Student',
        target_id=str(student_id),
        summary=f"Created student record {student_name} ({student_id})",
        outcome='SUCCESS',
        ip_address=request.remote_addr,
        details_json=f'{{"student_id": "{student_id}", "institution_id": {institution_id}, "programme": "{data.get("programme_name", "")}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'student': new_student.to_dict(), 'message': 'Student created successfully'}), 201

@students_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Strict isolation for Institute
    if user.role == 'institute' and student.institution_id != user.institution_id:
        return jsonify({'error': 'Forbidden', 'message': 'Cannot update students from other institutions'}), 403

    data = request.get_json() or {}
    reason = data.get('reason', 'Correction/Update via Portal').strip()

    changes = []
    
    if 'student_name' in data and data['student_name'] != student.student_name:
        changes.append(('student_name', student.student_name, data['student_name'].strip()))
        student.student_name = data['student_name'].strip()

    if 'enrolment_status' in data and data['enrolment_status'] != student.enrolment_status:
        changes.append(('enrolment_status', student.enrolment_status, data['enrolment_status']))
        student.enrolment_status = data['enrolment_status']

    if 'admission_category' in data and data['admission_category'] != student.admission_category:
        changes.append(('admission_category', student.admission_category, data['admission_category']))
        student.admission_category = data['admission_category']

    if 'supernumerary_status' in data:
        new_val = bool(data['supernumerary_status'])
        if new_val != student.supernumerary_status:
            changes.append(('supernumerary_status', str(student.supernumerary_status), str(new_val)))
            student.supernumerary_status = new_val

    if 'apaar_id' in data:
        raw_apaar = data['apaar_id'].strip()
        if raw_apaar:
            valid_format, cleaned_or_err = validate_apaar_format(raw_apaar)
            if not valid_format:
                return jsonify({'error': f"APAAR format error: {cleaned_or_err}"}), 400
            new_hmac = generate_apaar_hmac(cleaned_or_err)
            if new_hmac != student.apaar_id_hmac:
                changes.append(('apaar_id', student.apaar_id_masked, mask_apaar(cleaned_or_err)))
                student.apaar_id_hmac = new_hmac
                student.apaar_id_encrypted = encrypt_apaar(cleaned_or_err)
                student.apaar_id_masked = mask_apaar(cleaned_or_err)
                student.verification_status = 'pending'

    student.updated_at = datetime.utcnow()

    # Log each changed field in change history
    for field, old_val, new_val in changes:
        ch = RecordChangeHistory(
            student_id=student.id,
            changed_by_user_id=user.id,
            changed_by_name=user.full_name,
            change_type='manual_edit',
            field_name=field,
            old_value=str(old_val),
            new_value=str(new_val),
            reason=reason,
            timestamp=datetime.utcnow()
        )
        db.session.add(ch)

    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='STUDENT_RECORD_UPDATED',
        target_type='Student',
        target_id=str(student.student_id),
        summary=f"Updated student record {student.student_name} ({student.student_id}): {len(changes)} fields modified",
        outcome='SUCCESS',
        ip_address=request.remote_addr,
        details_json=f'{{"student_id": "{student.student_id}", "changes_count": {len(changes)}, "reason": "{reason}", "modified_fields": {[c["field"] for c in changes]}}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'student': student.to_dict(), 'message': 'Student updated successfully'}), 200

@students_bp.route('/export', methods=['GET'])
@jwt_required()
def export_students_csv():
    """Exports filtered student records with masked APAAR IDs to prevent sensitive data leakage."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = Student.query
    if user.role == 'institute':
        query = query.filter(Student.institution_id == user.institution_id)
    else:
        inst_id = request.args.get('institution_id', type=int)
        if inst_id:
            query = query.filter(Student.institution_id == inst_id)

    students = query.order_by(Student.student_name.asc()).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Student ID',
        'APAAR Identifier (Masked)',
        'Student Name',
        'Institution Name',
        'Programme',
        'Branch / Department',
        'Academic Year',
        'Admission Date',
        'Enrolment Status',
        'Category',
        'Supernumerary',
        'Verification Status',
        'Last Updated'
    ])

    for s in students:
        writer.writerow([
            s.student_id,
            s.apaar_id_masked or 'Not Assigned',
            s.student_name,
            s.institution.name if s.institution else 'N/A',
            s.programme_name,
            s.branch_or_department,
            s.academic_year,
            s.admission_date or '',
            s.enrolment_status,
            s.admission_category,
            'Yes' if s.supernumerary_status else 'No',
            s.verification_status,
            s.updated_at.strftime('%Y-%m-%d %H:%M') if s.updated_at else ''
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=student_records_{datetime.utcnow().strftime("%Y%m%d")}.csv'}
    )
