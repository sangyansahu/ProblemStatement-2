from datetime import datetime
from app.extensions import db

class Institution(db.Model):
    __tablename__ = 'institutions'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(100), default='Affiliated Engineering College')
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    principal_name = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False) # 'active', 'inactive', 'suspended'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', back_populates='institution', cascade='all, delete-orphan')
    students = db.relationship('Student', back_populates='institution', cascade='all, delete-orphan')
    programmes = db.relationship('Programme', back_populates='institution', cascade='all, delete-orphan')
    upload_batches = db.relationship('UploadBatch', back_populates='institution', cascade='all, delete-orphan')
    duplicate_cases = db.relationship('DuplicateReviewCase', foreign_keys='DuplicateReviewCase.institution_id', back_populates='institution', cascade='all, delete-orphan')

    def to_dict(self, include_stats=False):
        data = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'state': self.state,
            'district': self.district,
            'address': self.address,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'principal_name': self.principal_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_stats:
            data['student_count'] = len(self.students) if self.students else 0
            data['programme_count'] = len(self.programmes) if self.programmes else 0
            data['upload_count'] = len(self.upload_batches) if self.upload_batches else 0
        return data
