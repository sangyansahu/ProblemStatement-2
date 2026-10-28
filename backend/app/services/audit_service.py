import json
from datetime import datetime
from flask import request
from app.extensions import db
from app.models.audit import AuditLog

def sanitize_audit_details(details: dict) -> dict:
    if not isinstance(details, dict):
        return {'raw': str(details)}
    
    sanitized = {}
    forbidden_keys = {'password', 'password_hash', 'current_password', 'new_password', 'token', 'jwt', 'secret'}
    
    for k, v in details.items():
        if k.lower() in forbidden_keys:
            continue
        # Mask raw APAAR identifiers if present in details
        if 'apaar' in k.lower() and isinstance(v, str) and len(v) >= 12 and not 'masked' in k.lower():
            sanitized[k] = f"{v[:4]}-****-****-{v[-4:]}"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_audit_details(v)
        else:
            sanitized[k] = v
            
    return sanitized

def log_audit_event(
    actor=None,
    action: str = 'SYSTEM_ACTION',
    target_type: str = 'system',
    target_id: str = None,
    summary: str = '',
    details: dict = None,
    outcome: str = 'SUCCESS',
    ip_address: str = None
) -> AuditLog:
    """
    Centralized audit logging service adhering to Section 3.3.
    Records actor, action, target entity, concise summary, sanitized diffs, and outcome.
    """
    try:
        actor_id = actor.id if actor and hasattr(actor, 'id') else None
        actor_name = actor.full_name if actor and hasattr(actor, 'full_name') else 'System / Guest'
        actor_role = actor.role if actor and hasattr(actor, 'role') else 'system'
        
        if not ip_address:
            try:
                ip_address = request.remote_addr or '127.0.0.1'
            except Exception:
                ip_address = '127.0.0.1'

        cleaned_details = sanitize_audit_details(details or {})
        
        audit_entry = AuditLog(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            summary=summary[:254] if summary else f"{action.replace('_', ' ').title()} on {target_type}",
            outcome=outcome,
            ip_address=ip_address,
            details_json=json.dumps(cleaned_details),
            created_at=datetime.utcnow()
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        return audit_entry
    except Exception as e:
        db.session.rollback()
        print(f"[AUDIT LOGGING ERROR] Failed to record audit log: {e}")
        return None
