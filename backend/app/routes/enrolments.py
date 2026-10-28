from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.programme import Programme
from app.models.institution import Institution
from app.models.audit import AuditLog
from app.utils.auth_helper import get_current_user, role_required

enrolments_bp = Blueprint('enrolments', __name__, url_prefix='/api/v1/enrolments')

@enrolments_bp.route('/monitoring', methods=['GET'])
@jwt_required()
def get_enrolment_monitoring():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = Programme.query

    if user.role == 'institute':
        query = query.filter(Programme.institution_id == user.institution_id)
    else:
        inst_id = request.args.get('institution_id', type=int)
        if inst_id:
            query = query.filter(Programme.institution_id == inst_id)

    ay = request.args.get('academic_year', '').strip()
    if ay:
        query = query.filter(Programme.academic_year == ay)

    level = request.args.get('level', '').strip()
    if level:
        query = query.filter(Programme.level == level)

    programmes = query.all()
    results = [p.to_dict() for p in programmes]

    # Calculate aggregate summary
    total_approved = sum(p['approved_intake'] for p in results)
    total_enrolled = sum(p['actual_enrolment'] for p in results)
    overall_utilization = round((total_enrolled / total_approved * 100), 1) if total_approved > 0 else 0
    discrepancy_count = sum(1 for p in results if p['discrepancy_status'] == 'exceeds_approved_capacity')

    return jsonify({
        'programmes': results,
        'summary': {
            'total_programmes': len(results),
            'total_approved_intake': total_approved,
            'total_enrolled': total_enrolled,
            'overall_utilization_rate': overall_utilization,
            'discrepancy_count': discrepancy_count
        }
    }), 200

@enrolments_bp.route('/programmes', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def configure_programme_intake():
    user = get_current_user()
    data = request.get_json() or {}

    inst_id = data.get('institution_id')
    code = data.get('programme_code', '').strip().upper()
    name = data.get('programme_name', '').strip()
    branch = data.get('branch_or_department', '').strip()
    intake = data.get('approved_intake', 60)
    supernumerary = data.get('supernumerary_intake', 6)
    ay = data.get('academic_year', '2025-2026')

    if not inst_id or not code or not name or not branch:
        return jsonify({'error': 'institution_id, programme_code, programme_name, and branch_or_department are required'}), 400

    programme = Programme(
        institution_id=inst_id,
        programme_code=code,
        programme_name=name,
        branch_or_department=branch,
        level=data.get('level', 'UG'),
        academic_year=ay,
        approved_intake=intake,
        supernumerary_intake=supernumerary,
        is_demo_intake=False
    )
    db.session.add(programme)
    db.session.flush()

    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='PROGRAMME_INTAKE_CONFIGURED',
        target_type='programme',
        target_id=str(programme.id),
        details_json=f'{{"code": "{code}", "approved_intake": {intake}}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'programme': programme.to_dict(), 'message': 'Programme intake configured successfully'}), 201
