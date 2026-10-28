from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db
from app.models.user import User

def get_current_user():
    """Retrieves current authenticated User model instance from JWT identity."""
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if not identity:
            return None
        if isinstance(identity, dict):
            user_id = identity.get('id')
        else:
            user_id = int(identity)
        return db.session.get(User, user_id)
    except Exception:
        return None

def role_required(*allowed_roles):
    """
    Decorator enforcing that the authenticated user belongs to one of the specified roles.
    Example: @role_required('admin', 'super_admin')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
            if not user.is_active:
                return jsonify({'error': 'Forbidden', 'message': 'Account is inactive'}), 403
            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f"Access denied. Requires one of roles: {', '.join(allowed_roles)}. Your role: '{user.role}'."
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def institute_scope_guard(requested_institution_id: int = None) -> tuple[bool, str]:
    user = get_current_user()
    if not user:
        return False, "Authentication required"
    if user.role in ['admin', 'super_admin']:
        return True, ""
    if user.role == 'institute':
        if not user.institution_id:
            return False, "User account is not linked to any institution"
        if requested_institution_id and user.institution_id != requested_institution_id:
            return False, "Access denied: Institute accounts cannot access records from other institutions"
        return True, ""
    return False, "Role not permitted"
