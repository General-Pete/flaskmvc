from flask import Blueprint, jsonify, redirect
from flask_jwt_extended import jwt_required, current_user

from App.database import db
from App.models import Notification

notification_bp = Blueprint(
    "notifications",
    __name__
)

@notification_bp.route("/notifications")
@jwt_required()
def get_notifications():

    notifications = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%d %b %Y %H:%M")
        }
        for n in notifications
    ])

@notification_bp.route("/notifications/count")
@jwt_required()
def notification_count():

    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()

    return jsonify({
        "count": count
    })

@notification_bp.route("/notifications/<int:id>")
@jwt_required()
def open_notification(id):

    notification = Notification.query.get_or_404(id)

    if notification.user_id != current_user.id:
        return "Forbidden",403

    notification.is_read = True

    db.session.commit()

    return redirect(notification.link)