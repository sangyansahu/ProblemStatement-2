from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=True, index=True)
    role_target = db.Column(db.String(30), default='all', nullable=False) # 'all', 'institute', 'admin', 'super_admin'
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(20), default='info') # 'info', 'success', 'warning', 'critical'
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'institution_id': self.institution_id,
            'role_target': self.role_target,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
