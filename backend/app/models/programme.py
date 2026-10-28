from datetime import datetime
from app.extensions import db

class Programme(db.Model):
    __tablename__ = 'programmes'

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False, index=True)
    programme_code = db.Column(db.String(50), nullable=False) # e.g. "BTECH-CSE"
    programme_name = db.Column(db.String(150), nullable=False) # e.g. "Bachelor of Technology"
    branch_or_department = db.Column(db.String(150), nullable=False) # e.g. "Computer Science & Engineering"
    level = db.Column(db.String(50), default='UG') # 'UG', 'PG', 'Diploma', 'Doctoral'
    academic_year = db.Column(db.String(20), default='2025-2026', nullable=False)
    approved_intake = db.Column(db.Integer, default=60, nullable=False)
    supernumerary_intake = db.Column(db.Integer, default=6, nullable=False) # EWS / TFW / KM
    is_demo_intake = db.Column(db.Boolean, default=True) # Labels clearly if authoritative intake is simulated/demo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    institution = db.relationship('Institution', back_populates='programmes')
    students = db.relationship('Student', back_populates='programme')

    def to_dict(self):
        # Calculate actual enrolled count
        actual_enrolment = len(self.students) if self.students else 0
        total_capacity = self.approved_intake + self.supernumerary_intake
        utilization = round((actual_enrolment / self.approved_intake) * 100, 1) if self.approved_intake > 0 else 0
        
        discrepancy = 'normal'
        if actual_enrolment > total_capacity:
            discrepancy = 'exceeds_approved_capacity'
        elif actual_enrolment > self.approved_intake:
            discrepancy = 'supernumerary_utilized'
        elif utilization < 40:
            discrepancy = 'low_intake_utilization'

        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'institution_name': self.institution.name if self.institution else None,
            'institution_code': self.institution.code if self.institution else None,
            'programme_code': self.programme_code,
            'programme_name': self.programme_name,
            'branch_or_department': self.branch_or_department,
            'level': self.level,
            'academic_year': self.academic_year,
            'approved_intake': self.approved_intake,
            'supernumerary_intake': self.supernumerary_intake,
            'total_capacity': total_capacity,
            'actual_enrolment': actual_enrolment,
            'utilization_rate': utilization,
            'discrepancy_status': discrepancy,
            'is_demo_intake': self.is_demo_intake,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
