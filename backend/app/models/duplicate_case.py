from datetime import datetime
import json
from app.extensions import db

class DuplicateReviewCase(db.Model):
    __tablename__ = 'duplicate_review_cases'

    id = db.Column(db.Integer, primary_key=True)
    case_reference = db.Column(db.String(40), unique=True, nullable=False, index=True) # e.g. "DUP-2026-00109"
    issue_type = db.Column(db.String(60), nullable=False, index=True) 
    # 'student_id_collision', 'apaar_cross_institution', 'enrolment_overlap', 'transfer_record_discrepancy', 'repeated_import_conflict'
    severity = db.Column(db.String(20), default='caution', nullable=False) # 'critical', 'caution', 'notice'
    status = db.Column(db.String(40), default='open', nullable=False, index=True)
    # 'open', 'pending_institution_correction', 'resolved', 'dismissed', 'referred'

    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False, index=True)
    secondary_institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=True, index=True)
    
    student_id = db.Column(db.String(60), nullable=False)
    student_name = db.Column(db.String(150), nullable=True)
    apaar_id_masked = db.Column(db.String(30), nullable=True)
    
    description = db.Column(db.Text, nullable=False)
    details_json = db.Column(db.Text, nullable=True) # JSON with comparing record data
    
    resolution_decision = db.Column(db.String(60), nullable=True)
    # 'verified_valid_transfer', 'institution_corrected', 'record_merged_manually', 'false_positive_cleared', 'rejected_fraudulent'
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    institution = db.relationship('Institution', foreign_keys=[institution_id], back_populates='duplicate_cases')
    secondary_institution = db.relationship('Institution', foreign_keys=[secondary_institution_id])
    resolver = db.relationship('User', foreign_keys=[resolved_by_user_id])

    def to_dict(self):
        details = {}
        if self.details_json:
            try:
                details = json.loads(self.details_json)
            except Exception:
                details = {}

        return {
            'id': self.id,
            'case_reference': self.case_reference,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'status': self.status,
            'institution_id': self.institution_id,
            'institution_name': self.institution.name if self.institution else None,
            'institution_code': self.institution.code if self.institution else None,
            'secondary_institution_id': self.secondary_institution_id,
            'secondary_institution_name': self.secondary_institution.name if self.secondary_institution else None,
            'secondary_institution_code': self.secondary_institution.code if self.secondary_institution else None,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'apaar_id_masked': self.apaar_id_masked,
            'description': self.description,
            'details': details,
            'resolution_decision': self.resolution_decision,
            'resolution_notes': self.resolution_notes,
            'resolved_by': self.resolver.full_name if self.resolver else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
