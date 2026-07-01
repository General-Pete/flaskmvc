from App.database import db
from App.models import Notification
from App.models import User



def create_notification(
    user_id,
    title,
    message,
    link=None,
    commit=True
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        link=link
    )

    db.session.add(notification)

    if commit:
        db.session.commit()

    return notification

def create_notifications_bulk(users, title, message, link=None):
    notifications = []

    for user in users:
        notif = Notification(
            user_id=user.id,
            title=title,
            message=message,
            link=link
        )
        db.session.add(notif)
        notifications.append(notif)

    db.session.commit()
    return notifications

def notify_execs(title, message, link):
    execs = User.query.filter_by(role="Exec").all()

    for user in execs:
        create_notification(
            user.id,
            title,
            message,
            link,
            commit=False
        )

def notify_department_managers(
    department_id,
    title,
    message,
    link
):

    users = User.query.filter(
        User.department_id == department_id,
        User.role.in_(["Admin","Head"])
    ).all()

    for user in users:
        create_notification(
            user.id,
            title,
            message,
            link,
            commit=False
        )

def notify_assigned_user(task):

    if not task.assigned_user:
        return

    create_notification(
        task.assigned_user.id,
        "New Task Assigned",
        f"You have been assigned '{task.title}'.",
        f"/projects/{task.project_id}/tasks",
        commit=False
    )

def notify_department(
    department_id,
    title,
    message,
    link
):

    users = User.query.filter_by(
        department_id=department_id
    ).all()

    for user in users:
        create_notification(
            user.id,
            title,
            message,
            link,
            commit=False
        )