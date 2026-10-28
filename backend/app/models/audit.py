from datetime import datetime
import json
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, nullable=True)
    actor_name = db.Column(db.String(120), nullable=False)
    actor_role = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(100), nullable=False, index=True) # e.g. "STUDENT_RECORD_UPDATE", "CSV_IMPORT_COMMITTED"
    target_type = db.Column(db.String(50), nullable=False, index=True) # e.g. "student", "upload_batch", "duplicate_case"
    target_id = db.Column(db.String(100), nullable=True)
    summary = db.Column(db.String(255), nullable=True) # concise change summary
    outcome = db.Column(db.String(20), default='SUCCESS', nullable=False) # SUCCESS or FAILED
    ip_address = db.Column(db.String(50), nullable=True)
    details_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        details = {}
        if self.details_json:
            try:
                details = json.loads(self.details_json)
            except Exception:
                details = {'raw': self.details_json}

        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'actor_role': self.actor_role,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'summary': self.summary or details.get('summary') or f"{self.action.replace('_', ' ').title()} on {self.target_type}",
            'outcome': self.outcome or 'SUCCESS',
            'ip_address': self.ip_address or '127.0.0.1',
            'details': details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
