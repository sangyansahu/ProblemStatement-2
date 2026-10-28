from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.audit import AuditLog
from app.utils.auth_helper import role_required

audit_logs_bp = Blueprint('audit_logs', __name__, url_prefix='/api/v1/audit-logs')

@audit_logs_bp.route('', methods=['GET'])
@jwt_required()
@role_required('super_admin', 'admin')
def list_audit_logs():
    search = request.args.get('search', '').strip()
    action = request.args.get('action', '').strip()
    target = request.args.get('target_type', '').strip()
    outcome = request.args.get('outcome', '').strip()
    role = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = AuditLog.query

    if search:
        query = query.filter(
            (AuditLog.actor_name.ilike(f"%{search}%")) |
            (AuditLog.action.ilike(f"%{search}%")) |
            (AuditLog.target_type.ilike(f"%{search}%")) |
            (AuditLog.target_id.ilike(f"%{search}%")) |
            (AuditLog.summary.ilike(f"%{search}%"))
        )

    if action:
        query = query.filter(AuditLog.action == action)
    if target:
        query = query.filter(AuditLog.target_type.ilike(target))
    if outcome:
        query = query.filter(AuditLog.outcome == outcome)
    if role:
        query = query.filter(AuditLog.actor_role == role)

    query = query.order_by(AuditLog.created_at.desc())
    total = query.count()
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Distinct categories for frontend filter dropdowns
    actions = [r[0] for r in AuditLog.query.with_entities(AuditLog.action).distinct().all() if r[0]]
    target_types = [r[0] for r in AuditLog.query.with_entities(AuditLog.target_type).distinct().all() if r[0]]

    return jsonify({
        'logs': [l.to_dict() for l in paginated.items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages,
        'available_actions': sorted(actions),
        'available_targets': sorted(target_types)
    }), 200
