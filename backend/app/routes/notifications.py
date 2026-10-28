from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.notification import Notification
from app.utils.auth_helper import get_current_user

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = Notification.query.filter(
        (Notification.user_id == user.id) |
        (Notification.institution_id == user.institution_id) |
        (Notification.role_target.in_(['all', user.role]))
    )

    notifications = query.order_by(Notification.created_at.desc()).limit(30).all()
    unread_count = sum(1 for n in notifications if not n.is_read)

    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    }), 200

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    notif = Notification.query.get(notification_id)
    if not notif:
        return jsonify({'error': 'Notification not found'}), 404

    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True}), 200

@notifications_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    Notification.query.filter(
        (Notification.user_id == user.id) |
        (Notification.institution_id == user.institution_id) |
        (Notification.role_target.in_(['all', user.role]))
    ).update({'is_read': True}, synchronize_session=False)

    db.session.commit()
    return jsonify({'success': True}), 200
