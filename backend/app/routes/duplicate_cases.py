from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.duplicate_case import DuplicateReviewCase
from app.models.student import Student
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.utils.auth_helper import get_current_user

duplicate_cases_bp = Blueprint('duplicate_cases', __name__, url_prefix='/api/v1/duplicate-cases')

@duplicate_cases_bp.route('', methods=['GET'])
@jwt_required()
def list_duplicate_cases():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = DuplicateReviewCase.query

    # Enforce scoping: Institute sees cases involving their institution
    if user.role == 'institute':
        if not user.institution_id:
            return jsonify({'cases': [], 'total': 0}), 200
        query = query.filter(
            (DuplicateReviewCase.institution_id == user.institution_id) |
            (DuplicateReviewCase.secondary_institution_id == user.institution_id)
        )
    else:
        inst_id = request.args.get('institution_id', type=int)
        if inst_id:
            query = query.filter(
                (DuplicateReviewCase.institution_id == inst_id) |
                (DuplicateReviewCase.secondary_institution_id == inst_id)
            )

    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(DuplicateReviewCase.status == status)

    severity = request.args.get('severity', '').strip()
    if severity:
        query = query.filter(DuplicateReviewCase.severity == severity)

    cases = query.order_by(DuplicateReviewCase.detected_at.desc()).all()
    return jsonify({'cases': [c.to_dict() for c in cases], 'total': len(cases)}), 200

@duplicate_cases_bp.route('/<int:case_id>', methods=['GET'])
@jwt_required()
def get_duplicate_case(case_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    case = DuplicateReviewCase.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404

    if user.role == 'institute':
        if case.institution_id != user.institution_id and case.secondary_institution_id != user.institution_id:
            return jsonify({'error': 'Forbidden'}), 403

    return jsonify({'case': case.to_dict()}), 200

@duplicate_cases_bp.route('/<int:case_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_duplicate_case(case_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    case = DuplicateReviewCase.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404

    # Permission check: Institute can only submit explanation / mark corrected; Admin/Super Admin can resolve
    data = request.get_json() or {}
    decision = data.get('decision', '').strip()
    notes = data.get('notes', '').strip()

    if not decision or not notes:
        return jsonify({'error': 'Resolution decision and explanatory notes are required'}), 400

    if user.role == 'institute':
        # Institute provides explanation or marks for correction
        case.status = 'pending_institution_correction'
        case.resolution_notes = f"[INSTITUTE EXPLANATION by {user.full_name}]: {notes}"
    else:
        # Admin or Super Admin resolves the case
        case.status = 'resolved'
        case.resolution_decision = decision
        case.resolution_notes = f"[ADMIN RESOLUTION by {user.full_name} ({decision})]: {notes}"
        case.resolved_by_user_id = user.id
        case.resolved_at = datetime.utcnow()

        # Update student duplicate flag if resolved as false positive or valid transfer
        if decision in ['false_positive_cleared', 'verified_valid_transfer']:
            student = Student.query.filter_by(
                institution_id=case.institution_id,
                student_id=case.student_id
            ).first()
            if student:
                student.is_duplicate_flagged = False

    # Audit log
    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='DUPLICATE_CASE_RESOLUTION',
        target_type='duplicate_case',
        target_id=str(case.id),
        details_json=f'{{"case_ref": "{case.case_reference}", "decision": "{decision}", "status": "{case.status}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'case': case.to_dict(), 'message': 'Resolution recorded successfully'}), 200
