from datetime import datetime
from decimal import Decimal, InvalidOperation

from App.database import db
from App.models import (
    Project,
    Task,
    TaskNote,
    ProjectUpdateItem,
    ProjectRelationship,
    ActivityLog,
    User
)


PROJECT_STATUSES = [
    "Not Started",
    "In Progress",
    "On Hold",
    "Completed"
]

PROJECT_PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

TASK_STATUSES = [
    "To-Do",
    "In Progress",
    "Completed"
]


def parse_date(value):
    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_decimal(value):
    if not value:
        return None

    value = value.strip().replace(",", "")

    if not value:
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def parse_int(value):
    if value is None or value == "":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def money_display(value):
    if value is None:
        return "TBD"

    try:
        return f"${Decimal(value):,.2f}"
    except Exception:
        return "TBD"


def log_activity(entity_type, entity_id, action, details=None, user_id=None):
    log = ActivityLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details
    )

    db.session.add(log)


def is_admin(user):
    return user is not None and user.role == "Admin"


def is_exec(user):
    return user is not None and user.role == "Exec"


def is_normal_user(user):
    return user is not None and user.role == "User"


def get_all_users():
    return User.query.order_by(User.username.asc()).all()


def can_view_project(user, project):
    if not user or not project:
        return False

    if user.role in ["Admin", "Exec"]:
        return True

    return any(task.assigned_user_id == user.id for task in project.tasks)


def can_update_task(user, task):
    if not user or not task:
        return False

    if user.role == "Admin":
        return True

    return task.assigned_user_id == user.id


def get_visible_projects_for_user(user):
    if not user:
        return []

    if user.role in ["Admin", "Exec"]:
        return (
            Project.query
            .filter_by(is_archived=False)
            .order_by(Project.created_at.desc())
            .all()
        )

    return (
        Project.query
        .join(Task)
        .filter(Project.is_archived == False)
        .filter(Task.assigned_user_id == user.id)
        .distinct()
        .order_by(Project.created_at.desc())
        .all()
    )


def get_dashboard_context(user):
    projects = get_visible_projects_for_user(user)

    total_budget = Decimal("0.00")

    for project in projects:
        if project.budget_amount is not None:
            total_budget += Decimal(project.budget_amount)

    stats = {
        "project_count": len(projects),
        "in_progress_count": len([
            project for project in projects
            if project.status == "In Progress"
        ]),
        "high_priority_count": len([
            project for project in projects
            if project.priority in ["High", "Critical"]
        ]),
        "budget_display": money_display(total_budget) if total_budget > 0 else "TBD"
    }

    return {
        "projects": projects,
        "stats": stats
    }


def get_project_or_404(project_id):
    return Project.query.get_or_404(project_id)


def create_update_items_from_text(project_id, category, raw_text):
    if not raw_text:
        return

    lines = raw_text.splitlines()
    sort_order = 1

    for line in lines:
        text = line.strip()

        if not text:
            continue

        item = ProjectUpdateItem(
            project_id=project_id,
            category=category,
            text=text,
            sort_order=sort_order
        )

        db.session.add(item)
        sort_order += 1


def replace_update_items(project_id, category, raw_text):
    ProjectUpdateItem.query.filter_by(
        project_id=project_id,
        category=category
    ).delete()

    create_update_items_from_text(project_id, category, raw_text)


def create_project_from_form(form, user_id=None):
    name = form.get("name", "").strip()

    if not name:
        raise ValueError("Project name is required.")

    project = Project(
        name=name,
        description=form.get("description", "").strip() or None,
        project_type=form.get("project_type", "").strip() or None,
        current_focus=form.get("current_focus", "").strip() or None,
        status=form.get("status", "Not Started"),
        priority=form.get("priority", "Medium"),
        budget_amount=parse_decimal(form.get("budget_amount")),
        budget_tracker_value=form.get("budget_tracker_value", "").strip() or None,
        expected_outcome=form.get("expected_outcome", "").strip() or None,
        other_info=form.get("other_info", "").strip() or None,
        start_date=parse_date(form.get("start_date")),
        target_end_date=parse_date(form.get("target_end_date"))
    )

    db.session.add(project)
    db.session.flush()

    create_update_items_from_text(project.id, "Completed", form.get("completed_items", ""))
    create_update_items_from_text(project.id, "In Progress", form.get("in_progress_items", ""))
    create_update_items_from_text(project.id, "Risk", form.get("risk_items", ""))
    create_update_items_from_text(project.id, "Next Step", form.get("next_step_items", ""))

    log_activity(
        entity_type="Project",
        entity_id=project.id,
        action="Created",
        details=f"Project created: {project.name}",
        user_id=user_id
    )

    db.session.commit()

    return project


def update_project_from_form(project_id, form, user_id=None):
    project = get_project_or_404(project_id)

    name = form.get("name", "").strip()

    if not name:
        raise ValueError("Project name is required.")

    project.name = name
    project.description = form.get("description", "").strip() or None
    project.project_type = form.get("project_type", "").strip() or None
    project.current_focus = form.get("current_focus", "").strip() or None
    project.status = form.get("status", "Not Started")
    project.priority = form.get("priority", "Medium")
    project.budget_amount = parse_decimal(form.get("budget_amount"))
    project.budget_tracker_value = form.get("budget_tracker_value", "").strip() or None
    project.expected_outcome = form.get("expected_outcome", "").strip() or None
    project.other_info = form.get("other_info", "").strip() or None
    project.start_date = parse_date(form.get("start_date"))
    project.target_end_date = parse_date(form.get("target_end_date"))

    replace_update_items(project.id, "Completed", form.get("completed_items", ""))
    replace_update_items(project.id, "In Progress", form.get("in_progress_items", ""))
    replace_update_items(project.id, "Risk", form.get("risk_items", ""))
    replace_update_items(project.id, "Next Step", form.get("next_step_items", ""))

    log_activity(
        entity_type="Project",
        entity_id=project.id,
        action="Updated",
        details=f"Project updated: {project.name}",
        user_id=user_id
    )

    db.session.commit()

    return project


def get_project_detail_context(project_id, user):
    project = get_project_or_404(project_id)

    if not can_view_project(user, project):
        raise PermissionError("You do not have access to this project.")

    completed_tasks = [
        task for task in project.tasks
        if task.status == "Completed"
    ]

    in_progress_tasks = [
        task for task in project.tasks
        if task.status == "In Progress"
    ]

    todo_tasks = [
        task for task in project.tasks
        if task.status == "To-Do"
    ]

    other_info_items = []

    if project.other_info:
        other_info_items = [
            line.strip()
            for line in project.other_info.splitlines()
            if line.strip()
        ]

    if not other_info_items:
        other_info_items = [
            "No additional information has been recorded for this project."
        ]

    return {
        "project": project,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "todo_tasks": todo_tasks,
        "other_info_items": other_info_items,
        "can_edit_project": is_admin(user),
        "can_manage_tasks": is_admin(user)
    }


def get_project_edit_context(project_id):
    project = get_project_or_404(project_id)

    def category_text(category):
        return "\n".join([
            item.text for item in project.get_items_by_category(category)
        ])

    return {
        "project": project,
        "statuses": PROJECT_STATUSES,
        "priorities": PROJECT_PRIORITIES,
        "completed_items_text": category_text("Completed"),
        "in_progress_items_text": category_text("In Progress"),
        "risk_items_text": category_text("Risk"),
        "next_step_items_text": category_text("Next Step")
    }


def get_task_management_context(project_id, user):
    project = get_project_or_404(project_id)

    if not can_view_project(user, project):
        raise PermissionError("You do not have access to this project.")

    query = (
        Task.query
        .filter_by(project_id=project.id)
        .order_by(Task.created_at.desc())
    )

    if user.role == "User":
        query = query.filter(Task.assigned_user_id == user.id)

    tasks = query.all()

    users = get_all_users()

    return {
        "project": project,
        "tasks": tasks,
        "users": users,
        "task_statuses": TASK_STATUSES,
        "can_manage_tasks": is_admin(user),
        "can_edit_task_fields": is_admin(user),
        "can_add_task_notes": user.role in ["Admin", "User"]
    }


def create_task_from_form(project_id, form, user_id=None):
    project = get_project_or_404(project_id)

    title = form.get("title", "").strip()

    if not title:
        raise ValueError("Task title is required.")

    task = Task(
        project_id=project.id,
        title=title,
        description=form.get("description", "").strip() or None,
        status=form.get("status", "To-Do"),
        priority=form.get("priority", "Medium"),
        assigned_user_id=parse_int(form.get("assigned_user_id")),
        due_date=parse_date(form.get("due_date"))
    )

    db.session.add(task)
    db.session.flush()

    log_activity(
        entity_type="Task",
        entity_id=task.id,
        action="Created",
        details=f"Task created under project {project.name}: {task.title}",
        user_id=user_id
    )

    db.session.commit()

    return task


def update_task_from_form(task_id, form, user):
    task = Task.query.get_or_404(task_id)

    if not can_update_task(user, task):
        raise PermissionError("You cannot update this task.")

    old_status = task.status

    if user.role == "Admin":
        task.assigned_user_id = parse_int(form.get("assigned_user_id"))
        task.due_date = parse_date(form.get("due_date"))
        task.priority = form.get("priority", task.priority)

    task.status = form.get("status", task.status)

    log_activity(
        entity_type="Task",
        entity_id=task.id,
        action="Updated",
        details=f"Task updated. Old status: {old_status}, New status: {task.status}",
        user_id=user.id
    )

    db.session.commit()

    return task


def add_task_note(task_id, form, user):
    task = Task.query.get_or_404(task_id)

    if not can_update_task(user, task):
        raise PermissionError("You cannot add notes to this task.")

    note_text = form.get("note", "").strip()

    if not note_text:
        raise ValueError("Note cannot be empty.")

    note = TaskNote(
        task_id=task.id,
        user_id=user.id,
        note=note_text
    )

    db.session.add(note)

    log_activity(
        entity_type="TaskNote",
        entity_id=task.id,
        action="Created",
        details=f"Note added to task: {task.title}",
        user_id=user.id
    )

    db.session.commit()

    return note


def delete_task(task_id, user_id=None):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    task_title = task.title

    log_activity(
        entity_type="Task",
        entity_id=task.id,
        action="Deleted",
        details=f"Task deleted: {task_title}",
        user_id=user_id
    )

    db.session.delete(task)
    db.session.commit()

    return project_id


def get_project_report_context(project_id, user=None):
    project = get_project_or_404(project_id)

    # Keep this check if you already added role permissions.
    # It allows Admin/Exec/all valid assigned users depending on your can_view_project() logic.
    if user is not None:
        if not can_view_project(user, project):
            raise PermissionError("You do not have access to this project.")

    tasks = (
        Task.query
        .filter_by(project_id=project.id)
        .order_by(Task.created_at.asc())
        .all()
    )

    completed_tasks = [
        task for task in tasks
        if task.status == "Completed"
    ]

    in_progress_tasks = [
        task for task in tasks
        if task.status == "In Progress"
    ]

    todo_tasks = [
        task for task in tasks
        if task.status == "To-Do"
    ]

    task_stats = {
        "total": len(tasks),
        "todo": len(todo_tasks),
        "in_progress": len(in_progress_tasks),
        "completed": len(completed_tasks)
    }

    return {
        "project": project,

        "completed_items": project.get_items_by_category("Completed"),
        "in_progress_items": project.get_items_by_category("In Progress"),
        "risk_items": project.get_items_by_category("Risk"),
        "next_step_items": project.get_items_by_category("Next Step"),

        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "todo_tasks": todo_tasks,
        "task_stats": task_stats
    }