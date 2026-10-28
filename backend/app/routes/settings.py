from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.utils.auth_helper import role_required, get_current_user

settings_bp = Blueprint('settings', __name__, url_prefix='/api/v1/settings')

# In-memory runtime settings overlay with persistent config defaults
runtime_settings = {
    'current_academic_year': '2025-2026',
    'academic_years': ['2023-2024', '2024-2025', '2025-2026', '2026-2027'],
    'max_upload_size_mb': 16,
    'max_upload_rows': 50000,
    'verification_adapter_mode': 'Simulated Sandbox (Educational Mock Registry)',
    'is_official_api_active': False,
    'enrolment_statuses': ['Active', 'Completed', 'Dropped Out', 'Suspended', 'Transferred'],
    'admission_categories': ['General', 'OBC', 'SC', 'ST', 'EWS', 'Management', 'NRI'],
    'data_retention_days': 1825 # 5 years
}

@settings_bp.route('', methods=['GET'])
@jwt_required()
def get_settings():
    return jsonify({'settings': runtime_settings}), 200

@settings_bp.route('', methods=['PUT'])
@jwt_required()
@role_required('super_admin')
def update_settings():
    user = get_current_user()
    data = request.get_json() or {}

    if 'current_academic_year' in data:
        runtime_settings['current_academic_year'] = data['current_academic_year']
    if 'max_upload_size_mb' in data:
        runtime_settings['max_upload_size_mb'] = int(data['max_upload_size_mb'])
    if 'data_retention_days' in data:
        runtime_settings['data_retention_days'] = int(data['data_retention_days'])

    from app.services.audit_service import log_audit_event
    log_audit_event(
        actor=user,
        action='SYSTEM_SETTINGS_UPDATED',
        target_type='SystemSettings',
        target_id='global_config',
        summary=f"Super Admin updated operational parameters (Academic Year: {runtime_settings['current_academic_year']}, Max Upload: {runtime_settings['max_upload_size_mb']}MB)",
        outcome='SUCCESS',
        details={'updated_keys': list(data.keys())}
    )

    return jsonify({
        'settings': runtime_settings,
        'message': 'System settings updated successfully'
    }), 200
