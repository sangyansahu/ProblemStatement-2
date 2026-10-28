from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.user import User
from app.models.institution import Institution
from app.models.audit import AuditLog
from app.utils.auth_helper import get_current_user, role_required

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

@users_bp.route('', methods=['GET'])
@jwt_required()
@role_required('super_admin')
def list_users():
    role_filter = request.args.get('role', '').strip()
    search = request.args.get('search', '').strip()

    query = User.query
    if role_filter:
        query = query.filter(User.role == role_filter)
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    users = query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users], 'total': len(users)}), 200

@users_bp.route('', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def create_user():
    actor = get_current_user()
    data = request.get_json() or {}

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'institute')
    institution_id = data.get('institution_id')

    if not username or not email or not full_name or not password:
        return jsonify({'error': 'username, email, full_name, and password are required'}), 400

    if role not in ['institute', 'admin', 'super_admin']:
        return jsonify({'error': 'Invalid role specified'}), 400

    if role == 'institute' and not institution_id:
        return jsonify({'error': 'Institute users must be linked to an institution_id'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already in use'}), 409

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        institution_id=institution_id if role == 'institute' else None,
        is_active=True,
        created_at=datetime.utcnow()
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.flush()

    audit = AuditLog(
        actor_id=actor.id,
        actor_name=actor.full_name,
        actor_role=actor.role,
        action='USER_ACCOUNT_CREATED',
        target_type='user',
        target_id=str(new_user.id),
        details_json=f'{{"username": "{username}", "role": "{role}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'user': new_user.to_dict(), 'message': 'User created successfully'}), 201

@users_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@role_required('super_admin')
def toggle_user_status(user_id):
    actor = get_current_user()
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    if target_user.id == actor.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400

    data = request.get_json() or {}
    new_active = data.get('is_active', not target_user.is_active)
    target_user.is_active = new_active

    audit = AuditLog(
        actor_id=actor.id,
        actor_name=actor.full_name,
        actor_role=actor.role,
        action='USER_STATUS_TOGGLED',
        target_type='user',
        target_id=str(target_user.id),
        details_json=f'{{"username": "{target_user.username}", "is_active": {str(new_active).lower()}}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'user': target_user.to_dict(), 'message': f"User account {'activated' if new_active else 'deactivated'}."}), 200
