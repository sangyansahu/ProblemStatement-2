from datetime import datetime
from app.extensions import db

class RecordChangeHistory(db.Model):
    __tablename__ = 'record_change_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    changed_by_name = db.Column(db.String(120), nullable=False)
    change_type = db.Column(db.String(50), nullable=False) # 'creation', 'manual_edit', 'verification_update', 'duplicate_resolved'
    field_name = db.Column(db.String(80), nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    student = db.relationship('Student', back_populates='change_history')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'changed_by_user_id': self.changed_by_user_id,
            'changed_by_name': self.changed_by_name,
            'change_type': self.change_type,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
