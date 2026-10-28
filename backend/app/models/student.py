from datetime import datetime
from app.extensions import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False, index=True)
    student_id = db.Column(db.String(60), nullable=False, index=True) # Unique within institution
    
    # Sensitive APAAR fields
    apaar_id_encrypted = db.Column(db.Text, nullable=True)
    apaar_id_hmac = db.Column(db.String(64), nullable=True, index=True) # HMAC-SHA256
    apaar_id_masked = db.Column(db.String(30), nullable=True) # e.g. "APAAR-****-****-4821"

    student_name = db.Column(db.String(150), nullable=False, index=True)
    programme_id = db.Column(db.Integer, db.ForeignKey('programmes.id'), nullable=True, index=True)
    programme_name = db.Column(db.String(150), nullable=False)
    branch_or_department = db.Column(db.String(150), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False, index=True)
    admission_date = db.Column(db.String(20), nullable=True) # YYYY-MM-DD
    enrolment_status = db.Column(db.String(30), default='Active', nullable=False) # 'Active', 'Completed', 'Dropped Out', 'Suspended', 'Transferred'
    admission_category = db.Column(db.String(50), default='General') # 'General', 'OBC', 'SC', 'ST', 'EWS', 'Management', 'NRI'
    supernumerary_status = db.Column(db.Boolean, default=False, nullable=False)
    
    # Verification workflow
    verification_status = db.Column(db.String(40), default='pending', nullable=False, index=True)
    # Statuses: 'not_submitted', 'pending', 'verified', 'unable_to_verify', 'mismatch_detected', 'requires_manual_review', 'rejected'
    verification_source = db.Column(db.String(50), default='simulated') # 'simulated', 'manual_review', 'authorized_registry'
    verification_notes = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    is_duplicate_flagged = db.Column(db.Boolean, default=False, nullable=False)
    data_quality_issues_json = db.Column(db.Text, nullable=True)
    
    upload_batch_id = db.Column(db.Integer, db.ForeignKey('upload_batches.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    institution = db.relationship('Institution', back_populates='students')
    programme = db.relationship('Programme', back_populates='students')
    upload_batch = db.relationship('UploadBatch', back_populates='students')
    change_history = db.relationship('RecordChangeHistory', back_populates='student', cascade='all, delete-orphan')

    # Unique constraint per institution + student_id
    __table_args__ = (
        db.UniqueConstraint('institution_id', 'student_id', name='uq_institution_student_id'),
    )

    def to_dict(self, can_view_full_apaar=False):
        import json
        issues = []
        if self.data_quality_issues_json:
            try:
                issues = json.loads(self.data_quality_issues_json)
            except Exception:
                issues = []

        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'institution_name': self.institution.name if self.institution else None,
            'institution_code': self.institution.code if self.institution else None,
            'student_id': self.student_id,
            'apaar_id_masked': self.apaar_id_masked or 'Not Assigned',
            'apaar_id': self.apaar_id_masked if not can_view_full_apaar else (self.apaar_id_masked), # Always masked by default for privacy
            'student_name': self.student_name,
            'programme_id': self.programme_id,
            'programme_name': self.programme_name,
            'branch_or_department': self.branch_or_department,
            'academic_year': self.academic_year,
            'admission_date': self.admission_date,
            'enrolment_status': self.enrolment_status,
            'admission_category': self.admission_category,
            'supernumerary_status': self.supernumerary_status,
            'verification_status': self.verification_status,
            'verification_source': self.verification_source,
            'verification_notes': self.verification_notes,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'is_duplicate_flagged': self.is_duplicate_flagged,
            'data_quality_issues': issues,
            'upload_batch_id': self.upload_batch_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
