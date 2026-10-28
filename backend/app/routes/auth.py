from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from app.extensions import db
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.auth_helper import get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Bad Request', 'message': 'Username and password are required'}), 400

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Forbidden', 'message': 'This account has been deactivated. Contact AICTE administrator.'}), 403

    user.last_login = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action='USER_LOGIN',
        target_type='user',
        target_id=str(user.id),
        ip_address=request.remote_addr,
        details_json=f'{{"username": "{user.username}", "role": "{user.role}"}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )

    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired session'}), 401

    return jsonify({
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid session'}), 401

    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if not full_name:
        return jsonify({'error': 'Validation Error', 'message': 'Full name is required'}), 400
    if not email:
        return jsonify({'error': 'Validation Error', 'message': 'Email address is required'}), 400

    # Ensure email is unique across other users
    existing = User.query.filter(User.email == email, User.id != user.id).first()
    if existing:
        return jsonify({'error': 'Conflict', 'message': 'Email address is already in use by another account'}), 409

    old_values = {'full_name': user.full_name, 'email': user.email, 'phone': user.phone or ''}

    user.full_name = full_name
    user.email = email
    user.phone = phone

    db.session.commit()

    # Log audit event
    from app.services.audit_service import log_audit_event
    log_audit_event(
        actor=user,
        action='PROFILE_UPDATED',
        target_type='User',
        target_id=str(user.id),
        summary=f"User {user.username} updated profile information",
        details={'previous': old_values, 'updated': {'full_name': user.full_name, 'email': user.email, 'phone': user.phone}}
    )

    return jsonify({
        'user': user.to_dict(),
        'message': 'Profile details saved successfully'
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid session'}), 401

    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Validation Error', 'message': 'Current and new password are required'}), 400

    if not user.check_password(current_password):
        from app.services.audit_service import log_audit_event
        log_audit_event(
            actor=user,
            action='PASSWORD_CHANGE_FAILED',
            target_type='User',
            target_id=str(user.id),
            summary="Failed password change attempt: Incorrect current password",
            outcome='FAILED'
        )
        return jsonify({'error': 'Unauthorized', 'message': 'Current password does not match'}), 401

    if len(new_password) < 6:
        return jsonify({'error': 'Validation Error', 'message': 'New password must be at least 6 characters'}), 400

    user.set_password(new_password)
    db.session.commit()

    from app.services.audit_service import log_audit_event
    log_audit_event(
        actor=user,
        action='PASSWORD_CHANGED',
        target_type='User',
        target_id=str(user.id),
        summary=f"User {user.username} successfully updated account password"
    )

    return jsonify({
        'message': 'Password updated successfully'
    }), 200

@auth_bp.route('/switch-demo-role', methods=['POST'])
def switch_demo_role():
    """
    Demo/Evaluation helper: allows instant switching between Institute, Admin, and Super Admin
    demo personas to demonstrate permissions and interfaces effortlessly.
    """
    data = request.get_json() or {}
    target_role = data.get('role', 'institute')

    if target_role not in ['institute', 'admin', 'super_admin']:
        return jsonify({'error': 'Invalid role'}), 400

    user = User.query.filter_by(role=target_role).first()
    if not user:
        return jsonify({'error': 'Seed user for role not found'}), 404

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )

    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'message': f"Switched to {user.full_name} ({target_role.upper()})"
    }), 200
