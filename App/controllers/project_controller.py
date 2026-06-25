from datetime import datetime
from decimal import Decimal, InvalidOperation

from App.database import db
from App.models import (
    Department,
    Project,
    Milestone,
    Task,
    TaskNote,
    ProjectUpdateItem,
    ProjectRelationship,
    ActivityLog,
    User
)

def get_all_departments():
    return (
        Department.query
        .filter_by(is_active=True)
        .order_by(Department.name.asc())
        .all()
    )


def is_admin(user):
    return user is not None and user.role == "Admin"


def is_exec(user):
    return user is not None and user.role == "Exec"


def is_normal_user(user):
    return user is not None and user.role == "User"

def is_head(user):
    return user is not None and user.role =="Head"


def can_head_manage_department(user, department_id):
    if not user:
        return False

    if user.role not in ["Admin", "Head"]:
        return False
    

    return user.department_id == department_id



def can_view_project(user, project):
    if not user or not project:
        return False

    if user.role == "Exec":
        return True

    if user.role in ["Admin","Head"]:
        return user.department_id == project.department_id

    # Normal user only sees projects where they have an assigned task.
    return any(task.assigned_user_id == user.id for task in project.tasks)

 


def can_manage_project(user, project):
    if not user or not project:
        return False

    if user.role not in [ "Admin", "Head"]:
        return False
    

    return user.department_id == project.department_id


def can_update_task(user, task):
    if not user or not task:
        return False

    if user.role in ["Admin","Head"]:
        return user.department_id == task.project.department_id


    if user.role == "User":
        return task.assigned_user_id == user.id

    return False


def get_visible_projects_for_user(user, selected_department_id=None):
    if not user:
        return []

    query = Project.query.filter(Project.is_archived == False)

    if user.role == "Exec":
        if selected_department_id:
            query = query.filter(Project.department_id == selected_department_id)

        return query.order_by(Project.created_at.desc()).all()

    if user.role in ["Admin","Head"]:
        return (
            query
            .filter(Project.department_id == user.department_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    
    return (
        query
        .join(Task)
        .filter(Task.assigned_user_id == user.id)
        .distinct()
        .order_by(Project.created_at.desc())
        .all()
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

def is_head(user):
    return user is not None and user.role == "Head"


def get_all_users():
    return User.query.order_by(User.username.asc()).all()


def can_view_project(user, project):
    if not user or not project:
        return False

    if user.role in ["Admin", "Head","Exec"]:
        return True

    return any(task.assigned_user_id == user.id for task in project.tasks)


def can_update_task(user, task):
    if not user or not task:
        return False

    if user.role in ["Admin","Head"]:
        return True

   
    
    return task.assigned_user_id == user.id


def get_visible_projects_for_user(user, selected_department_id=None):
    if not user:
        return []

    query = Project.query.filter(Project.is_archived == False)

    # Executive sees all departments, or one selected department
    if user.role == "Exec":
        if selected_department_id:
            query = query.filter(Project.department_id == selected_department_id)

        return (
            query
            .order_by(Project.created_at.desc())
            .all()
        )

    # Department Admin/Head sees all projects in their own department only
    if user.role in ["Admin","Head"]:
        return (
            query
            .filter(Project.department_id == user.department_id)
            .order_by(Project.created_at.desc())
            .all()
        )



    # Normal user sees only projects where they have assigned tasks
    return (
        query
        .join(Task)
        .filter(Task.assigned_user_id == user.id)
        .distinct()
        .order_by(Project.created_at.desc())
        .all()
    )

def get_all_departments():
    return (
        Department.query
        .filter_by(is_active=True)
        .order_by(Department.name.asc())
        .all()
    )

def get_dashboard_context(user, selected_department_id=None):
    projects = get_visible_projects_for_user(
        user,
        selected_department_id
    )

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
        "stats": stats,
        "departments": get_all_departments(),
        "selected_department_id": selected_department_id
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


def create_project_from_form(form, current_user):
    name = form.get("name", "").strip()

    if not name:
        raise ValueError("Project name is required.")
    
    if not current_user or current_user.role not in ["Admin","Head"]:
        raise PermissionError("Only department admins and heads can create projects.")

    if not current_user.department_id:
        raise ValueError("Your account is not assigned to a department.")

    project = Project(
        name=name,
        description=form.get("description", "").strip() or None,
        project_type=form.get("project_type", "").strip() or None,
        current_focus=form.get("current_focus", "").strip() or None,
        status=form.get("status", "Not Started"),
        priority=form.get("priority", "Medium"),
        department_id=current_user.department_id,
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
        user_id=current_user.id
    )

    db.session.commit()

    return project


def update_project_from_form(project_id, form, current_user):
    project = get_project_or_404(project_id)

    if not can_manage_project(current_user, project):
        raise PermissionError("You cannot edit this project.")

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
        user_id=current_user.id
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
        "department": project.department,
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

    users = (
        User.query
        .filter(User.department_id == project.department_id)
        .order_by(User.username.asc())
        .all()
    )

    milestones = (
        Milestone.query
        .filter_by(project_id=project.id)
        .order_by(Milestone.created_at.asc())
        .all()
    )

    return {
        "project": project,
        "tasks": tasks,
        "users": users,
        "milestones": milestones,
        "task_statuses": TASK_STATUSES,
        "can_manage_tasks": can_manage_project(user, project),
        "can_edit_task_fields": can_manage_project(user, project),
        "can_add_task_notes": user.role in ["Admin", "User"]
    }


def create_task_from_form(project_id, form, current_user):
    project = get_project_or_404(project_id)

    if not can_manage_project(current_user, project):
        raise PermissionError("You cannot create tasks for this project.")

    title = form.get("title", "").strip()

    if not title:
        raise ValueError("Task title is required.")

    assigned_user_id = parse_int(form.get("assigned_user_id"))
    milestone_id = parse_int(form.get("milestone_id"))

    if assigned_user_id:
        assigned_user = User.query.get(assigned_user_id)

        if not assigned_user:
            raise ValueError("Assigned user does not exist.")

        if assigned_user.department_id != project.department_id:
            raise ValueError("Assigned user must belong to the same department as the project.")
        
    if milestone_id:
        milestone = Milestone.query.get(milestone_id)

        if not milestone:
            raise ValueError("Selected milestone does not exist.")

        if milestone.project_id != project.id:
            raise ValueError("Selected milestone does not belong to this project.")

    task = Task(
        project_id=project.id,
        milestone_id=milestone_id,
        title=title,
        description=form.get("description", "").strip() or None,
        status=form.get("status", "To-Do"),
        priority=form.get("priority", "Medium"),
        assigned_user_id=assigned_user_id,
        due_date=parse_date(form.get("due_date"))
    )

    db.session.add(task)
    db.session.flush()

    log_activity(
        entity_type="Task",
        entity_id=task.id,
        action="Created",
        details=f"Task created under project {project.name}: {task.title}",
        user_id=current_user.id
    )

    db.session.commit()

    return task


def update_task_from_form(task_id, form, user):
    task = Task.query.get_or_404(task_id)

    if not can_update_task(user, task):
        raise PermissionError("You cannot update this task.")

    old_status = task.status

    if user.role in ["Admin", "Head"]:
        task.assigned_user_id = parse_int(form.get("assigned_user_id"))
        task.due_date = parse_date(form.get("due_date"))
        task.priority = form.get("priority", task.priority)

        milestone_id = parse_int(form.get("milestone_id"))

        if milestone_id:
            milestone = Milestone.query.get(milestone_id)

            if not milestone:
                raise ValueError("Selected milestone does not exist.")

            if milestone.project_id != task.project_id:
                raise ValueError("Selected milestone does not belong to this project.")

            task.milestone_id = milestone.id
        else:
            task.milestone_id = None

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

    if user is not None:
        if not can_view_project(user, project):
            raise PermissionError("You do not have access to this project.")

    tasks = (
        Task.query
        .filter_by(project_id=project.id)
        .order_by(Task.created_at.asc())
        .all()
    )

    milestones = (
        Milestone.query
        .filter_by(project_id=project.id)
        .order_by(Milestone.created_at.asc())
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
        "milestones": milestones,

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


# =========================================================
# Milestone Management
# =========================================================

def get_milestone_or_404(milestone_id):
    return Milestone.query.get_or_404(milestone_id)


def get_milestone_management_context(project_id, user):
    project = get_project_or_404(project_id)

    if not can_view_project(user, project):
        raise PermissionError("You do not have access to this project.")

    # Only department admins can manage milestones.
    can_manage_milestones = can_manage_project(user, project)

    milestones = (
        Milestone.query
        .filter_by(project_id=project.id)
        .order_by(Milestone.created_at.asc())
        .all()
    )

    # Tasks without any milestone, useful for later UI display.
    unassigned_tasks = (
        Task.query
        .filter_by(project_id=project.id, milestone_id=None)
        .order_by(Task.created_at.desc())
        .all()
    )

    return {
        "project": project,
        "milestones": milestones,
        "unassigned_tasks": unassigned_tasks,
        "can_manage_milestones": can_manage_milestones
    }


def create_milestone_from_form(project_id, form, current_user):
    project = get_project_or_404(project_id)

    if not can_manage_project(current_user, project):
        raise PermissionError("You cannot create milestones for this project.")

    title = form.get("title", "").strip()
    description = form.get("description", "").strip() or None
    target_date = parse_date(form.get("target_date"))

    if not title:
        raise ValueError("Milestone title is required.")

    milestone = Milestone(
        project_id=project.id,
        title=title,
        description=description,
        target_date=target_date
    )

    db.session.add(milestone)
    db.session.flush()

    log_activity(
        entity_type="Milestone",
        entity_id=milestone.id,
        action="Created",
        details=f"Milestone created under project {project.name}: {milestone.title}",
        user_id=current_user.id
    )

    db.session.commit()

    return milestone


def update_milestone_from_form(milestone_id, form, current_user):
    milestone = get_milestone_or_404(milestone_id)
    project = milestone.project

    if not can_manage_project(current_user, project):
        raise PermissionError("You cannot edit this milestone.")

    title = form.get("title", "").strip()
    description = form.get("description", "").strip() or None
    target_date = parse_date(form.get("target_date"))

    if not title:
        raise ValueError("Milestone title is required.")

    milestone.title = title
    milestone.description = description
    milestone.target_date = target_date

    log_activity(
        entity_type="Milestone",
        entity_id=milestone.id,
        action="Updated",
        details=f"Milestone updated: {milestone.title}",
        user_id=current_user.id
    )

    db.session.commit()

    return milestone


def delete_milestone(milestone_id, current_user):
    milestone = get_milestone_or_404(milestone_id)
    project = milestone.project
    project_id = project.id
    milestone_title = milestone.title

    if not can_manage_project(current_user, project):
        raise PermissionError("You cannot delete this milestone.")

    # Preserve tasks. They are not deleted.
    # They are simply detached from the milestone.
    for task in milestone.tasks:
        task.milestone_id = None

    log_activity(
        entity_type="Milestone",
        entity_id=milestone.id,
        action="Deleted",
        details=f"Milestone deleted: {milestone_title}. Related tasks were left in place and detached.",
        user_id=current_user.id
    )

    db.session.delete(milestone)
    db.session.commit()

    return project_id