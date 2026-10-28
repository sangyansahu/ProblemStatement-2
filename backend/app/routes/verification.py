from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.student import Student
from app.services.verification_service import trigger_student_verification, manual_verification_override
from app.utils.auth_helper import get_current_user, role_required

verification_bp = Blueprint('verification', __name__, url_prefix='/api/v1/verification')

@verification_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_verification_queue():
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

    # Queue defaults to non-verified states
    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter(Student.verification_status == status_filter)
    else:
        query = query.filter(Student.verification_status.in_(['pending', 'requires_manual_review', 'mismatch_detected', 'unable_to_verify']))

    students = query.order_by(Student.created_at.desc()).limit(150).all()
    return jsonify({'queue': [s.to_dict() for s in students]}), 200

@verification_bp.route('/verify/<int:student_id>', methods=['POST'])
@jwt_required()
def verify_student(student_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if user.role == 'institute' and student.institution_id != user.institution_id:
        return jsonify({'error': 'Forbidden'}), 403

    res = trigger_student_verification(student_id, user_id=user.id, user_name=user.full_name)
    return jsonify(res), 200

@verification_bp.route('/manual-override', methods=['POST'])
@jwt_required()
@role_required('admin', 'super_admin')
def manual_override():
    user = get_current_user()
    data = request.get_json() or {}
    student_id = data.get('student_id')
    new_status = data.get('status') # 'verified', 'rejected', 'requires_manual_review', 'unable_to_verify'
    notes = data.get('notes', '').strip()

    if not student_id or not new_status or not notes:
        return jsonify({'error': 'student_id, status, and notes explaining the decision are required'}), 400

    res = manual_verification_override(
        student_id_db=student_id,
        new_status=new_status,
        notes=notes,
        user_id=user.id,
        user_name=user.full_name
    )
    return jsonify(res), 200

@verification_bp.route('/batch-verify', methods=['POST'])
@jwt_required()
def batch_verify():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = Student.query.filter(Student.verification_status.in_(['pending', 'not_submitted']))
    if user.role == 'institute':
        query = query.filter(Student.institution_id == user.institution_id)

    pending_students = query.limit(50).all()
    verified_count = 0
    flagged_count = 0

    for s in pending_students:
        res = trigger_student_verification(s.id, user_id=user.id, user_name=user.full_name)
        if res.get('verification_status') == 'verified':
            verified_count += 1
        else:
            flagged_count += 1

    return jsonify({
        'processed': len(pending_students),
        'verified_count': verified_count,
        'flagged_count': flagged_count,
        'message': f"Batch verification processed {len(pending_students)} records."
    }), 200
