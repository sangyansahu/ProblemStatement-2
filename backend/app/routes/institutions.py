from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.student import Student
from app.models.upload import UploadBatch
from app.models.audit import AuditLog
from app.utils.auth_helper import get_current_user, role_required

institutions_bp = Blueprint('institutions', __name__, url_prefix='/api/v1/institutions')

@institutions_bp.route('', methods=['GET'])
@jwt_required()
def list_institutions():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    # Institute role is strictly isolated to own institution
    if user.role == 'institute':
        if not user.institution_id:
            return jsonify({'institutions': [], 'total': 0}), 200
        inst = Institution.query.get(user.institution_id)
        return jsonify({
            'institutions': [inst.to_dict(include_stats=True)] if inst else [],
            'total': 1 if inst else 0,
            'page': 1,
            'pages': 1
        }), 200

    # Admin and Super Admin can query all institutions
    search = request.args.get('search', '').strip()
    state = request.args.get('state', '').strip()
    itype = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)

    query = Institution.query
    if search:
        query = query.filter(
            (Institution.name.ilike(f"%{search}%")) |
            (Institution.code.ilike(f"%{search}%")) |
            (Institution.district.ilike(f"%{search}%"))
        )
    if state:
        query = query.filter(Institution.state == state)
    if itype:
        query = query.filter(Institution.type == itype)
    if status:
        query = query.filter(Institution.status == status)

    query = query.order_by(Institution.name.asc())
    total = query.count()
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'institutions': [i.to_dict(include_stats=True) for i in paginated.items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages
    }), 200

@institutions_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_institution():
    user = get_current_user()
    if not user or not user.institution_id:
        return jsonify({'error': 'No institution associated with this user'}), 404
    return get_institution(user.institution_id)

@institutions_bp.route('/<int:institution_id>', methods=['GET'])
@jwt_required()
def get_institution(institution_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    # Security check: Institute user cannot inspect another institution
    if user.role == 'institute' and user.institution_id != institution_id:
        return jsonify({'error': 'Forbidden', 'message': 'Access to other institution details is prohibited.'}), 403

    inst = Institution.query.get(institution_id)
    if not inst:
        return jsonify({'error': 'Institution not found'}), 404

    data = inst.to_dict(include_stats=True)
    # Include programmes and recent uploads
    data['programmes'] = [p.to_dict() for p in inst.programmes]
    data['recent_uploads'] = [u.to_dict() for u in UploadBatch.query.filter_by(institution_id=institution_id).order_by(UploadBatch.created_at.desc()).limit(5).all()]
    
    # Verification breakdown for this institution
    verified_count = Student.query.filter_by(institution_id=institution_id, verification_status='verified').count()
    pending_count = Student.query.filter_by(institution_id=institution_id, verification_status='pending').count()
    discrepancy_count = Student.query.filter(
        Student.institution_id == institution_id,
        Student.verification_status.in_(['mismatch_detected', 'unable_to_verify', 'requires_manual_review'])
    ).count()

    data['verification_summary'] = {
        'verified': verified_count,
        'pending': pending_count,
        'discrepancy': discrepancy_count,
        'total': len(inst.students)
    }

    return jsonify({'institution': data}), 200

@institutions_bp.route('', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def create_institution():
    user = get_current_user()
    data = request.get_json() or {}

    code = data.get('code', '').strip().upper()
    name = data.get('name', '').strip()
    state = data.get('state', '').strip()
    district = data.get('district', '').strip()

    if not code or not name or not state or not district:
        return jsonify({'error': 'Missing required fields: code, name, state, district'}), 400

    if Institution.query.filter_by(code=code).first():
        return jsonify({'error': f"Institution code '{code}' already exists"}), 409

    inst = Institution(
        code=code,
        name=name,
        type=data.get('type', 'Affiliated Engineering College'),
        state=state,
        district=district,
        address=data.get('address', ''),
        contact_email=data.get('contact_email', ''),
        contact_phone=data.get('contact_phone', ''),
        principal_name=data.get('principal_name', ''),
        status=data.get('status', 'active')
    )
    db.session.add(inst)
    db.session.flush()

    # Audit log
    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='INSTITUTION_CREATED',
        target_type='institution',
        target_id=str(inst.id),
        details_json=f'{{"code": "{code}", "name": "{name}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'institution': inst.to_dict(), 'message': 'Institution created successfully'}), 201

@institutions_bp.route('/<int:institution_id>', methods=['PUT'])
@jwt_required()
@role_required('super_admin')
def update_institution(institution_id):
    user = get_current_user()
    inst = Institution.query.get(institution_id)
    if not inst:
        return jsonify({'error': 'Institution not found'}), 404

    data = request.get_json() or {}
    if 'name' in data:
        inst.name = data['name'].strip()
    if 'type' in data:
        inst.type = data['type'].strip()
    if 'state' in data:
        inst.state = data['state'].strip()
    if 'district' in data:
        inst.district = data['district'].strip()
    if 'address' in data:
        inst.address = data['address'].strip()
    if 'contact_email' in data:
        inst.contact_email = data['contact_email'].strip()
    if 'contact_phone' in data:
        inst.contact_phone = data['contact_phone'].strip()
    if 'principal_name' in data:
        inst.principal_name = data['principal_name'].strip()
    if 'status' in data:
        inst.status = data['status'].strip() # 'active', 'inactive', 'suspended'

    inst.updated_at = datetime.utcnow()

    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='INSTITUTION_UPDATED',
        target_type='institution',
        target_id=str(inst.id),
        details_json=f'{{"code": "{inst.code}", "status": "{inst.status}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'institution': inst.to_dict(), 'message': 'Institution updated successfully'}), 200
