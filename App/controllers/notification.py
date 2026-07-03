from App.database import db
from App.models import Notification
from App.models import User
from App.models import Project
from App.models import Task 
from datetime import date, timedelta 


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
def create_deadline_notifications():

    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    projects = Project.query.filter_by(
        is_archived=False
    ).all()

    for project in projects:

        if not project.target_end_date:
            continue

        # -------------------------
        # Due Tomorrow
        # -------------------------
        if project.target_end_date == tomorrow:

            users = User.query.filter_by(
                department_id=project.department_id
            ).all()

            for user in users:

                existing = Notification.query.filter_by(
                    user_id=user.id,
                    title="Project Due Tomorrow",
                    link=f"/projects/{project.id}"
                ).first()

                if not existing:

                    create_notification(
                        user.id,
                        "Project Due Tomorrow",
                        f"'{project.name}' is due tomorrow!",
                        f"/projects/{project.id}",
                        commit=False
                    )

        # -------------------------
        # Due Today
        # -------------------------
        if project.target_end_date == today:

            users = User.query.filter_by(
                department_id=project.department_id
            ).all()

            for user in users:

                existing = Notification.query.filter_by(
                    user_id=user.id,
                    title="Project Due Today",
                    link=f"/projects/{project.id}"
                ).first()

                if not existing:

                    create_notification(
                        user.id,
                        "Project Due Today",
                        f"'{project.name}' is due today!",
                        f"/projects/{project.id}",
                        commit=False
                    )

        # -------------------------
        # Overdue
        # -------------------------
        if project.target_end_date < today:

            users = User.query.filter_by(
                department_id=project.department_id
            ).all()

            days_overdue = (today - project.target_end_date).days

            for user in users:

                existing = Notification.query.filter_by(
                    user_id=user.id,
                    title="Project Overdue",
                    link=f"/projects/{project.id}"
                ).first()

                if not existing:

                    create_notification(
                        user.id,
                        "Project Overdue",
                        f"'{project.name}' is overdue by {days_overdue} days(s)",
                        f"/projects/{project.id}",
                        commit=False
                    ) 

         # -------------------------
        # Due in 7 Days 
        # -------------------------
        if project.target_end_date == next_week:

            users = User.query.filter_by(
                department_id=project.department_id
            ).all()

            for user in users:

                existing = Notification.query.filter_by(
                    user_id=user.id,
                    title="Project due in a week",
                    link=f"/projects/{project.id}"
                ).first()

                if not existing:

                    create_notification(
                        user.id,
                        "Project Due in a week",
                        f"'{project.name}' is due in one week",
                        f"/projects/{project.id}",
                        commit=False
                    )                                  

    db.session.commit()


def create_task_deadline_notifications():

    today = date.today()
    tomorrow = today + timedelta(days=1)

    tasks = Task.query.all()

    for task in tasks:

        # Ignore tasks without a due date
        if not task.due_date:
            continue

        # Ignore tasks with nobody assigned
        if not task.assigned_user:
            continue

        # Ignore completed tasks
        if task.status == "Completed":
            continue

        # -------------------------
        # Due Tomorrow
        # -------------------------
        if task.due_date == tomorrow:

            existing = Notification.query.filter_by(
                user_id=task.assigned_user.id,
                title="Task Due Tomorrow",
                link=f"/projects/{task.project_id}/tasks"
            ).first()

            if not existing:

                create_notification(
                    task.assigned_user.id,
                    "Task Due Tomorrow",
                    f"'{task.title}' is due tomorrow.",
                    f"/projects/{task.project_id}/tasks",
                    commit=False
                )

        # -------------------------
        # Due Today
        # -------------------------
        if task.due_date == today:

            existing = Notification.query.filter_by(
                user_id=task.assigned_user.id,
                title="Task Due Today",
                link=f"/projects/{task.project_id}/tasks"
            ).first()

            if not existing:

                create_notification(
                    task.assigned_user.id,
                    "Task Due Today",
                    f"'{task.title}' is due today.",
                    f"/projects/{task.project_id}/tasks",
                    commit=False
                )

        # -------------------------
        # Overdue
        # -------------------------
        if task.due_date < today:

            days_overdue = (today - task.due_date).days

            existing = Notification.query.filter_by(
                user_id=task.assigned_user.id,
                title="Task Overdue",
                link=f"/projects/{task.project_id}/tasks"
            ).first()

            if not existing:

                create_notification(
                    task.assigned_user.id,
                    "Task Overdue",
                    f"'{task.title}' is overdue by {days_overdue} day(s).",
                    f"/projects/{task.project_id}/tasks",
                    commit=False
                )

    db.session.commit()