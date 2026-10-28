from datetime import datetime
import json
from app.extensions import db

class UploadBatch(db.Model):
    __tablename__ = 'upload_batches'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(40), unique=True, nullable=False, index=True) # e.g. "UB-2026-00412"
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_size_bytes = db.Column(db.Integer, default=0)
    total_rows = db.Column(db.Integer, default=0)
    valid_rows = db.Column(db.Integer, default=0)
    invalid_rows = db.Column(db.Integer, default=0)
    warning_rows = db.Column(db.Integer, default=0)
    duplicate_rows = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='completed', nullable=False) # 'uploaded', 'processing', 'completed', 'failed'
    error_report_json = db.Column(db.Text, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    institution = db.relationship('Institution', back_populates='upload_batches')
    uploader = db.relationship('User', foreign_keys=[created_by_user_id])
    students = db.relationship('Student', back_populates='upload_batch')

    def to_dict(self, include_errors=False):
        errors = []
        if include_errors and self.error_report_json:
            try:
                errors = json.loads(self.error_report_json)
            except Exception:
                errors = []

        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'institution_id': self.institution_id,
            'institution_name': self.institution.name if self.institution else None,
            'institution_code': self.institution.code if self.institution else None,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'file_size_kb': round(self.file_size_bytes / 1024, 1) if self.file_size_bytes else 0,
            'total_rows': self.total_rows,
            'valid_rows': self.valid_rows,
            'invalid_rows': self.invalid_rows,
            'warning_rows': self.warning_rows,
            'duplicate_rows': self.duplicate_rows,
            'status': self.status,
            'error_report': errors if include_errors else None,
            'error_count': len(errors) if errors else self.invalid_rows,
            'created_by': self.uploader.full_name if self.uploader else 'System User',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
