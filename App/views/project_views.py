from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_jwt_extended import jwt_required, current_user

from App.controllers.project_controller import (
    PROJECT_STATUSES,
    PROJECT_PRIORITIES,
    get_dashboard_context,
    create_project_from_form,
    update_project_from_form,
    get_project_edit_context,
    get_project_detail_context,
    get_task_management_context,
    create_task_from_form,
    update_task_from_form,
    delete_task,
    add_task_note,
    get_project_report_context
)


projects_bp = Blueprint(
    "projects",
    __name__,
    template_folder="../templates"
)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user or current_user.role != "Admin":
            flash("Admins only.", "error")
            return redirect(url_for("projects.dashboard"))

        return fn(*args, **kwargs)

    return wrapper


@projects_bp.route("/projects")
@jwt_required()
def dashboard():
    selected_department_id = request.args.get("department_id", type=int)

    context = get_dashboard_context(
        current_user,
        selected_department_id=selected_department_id
    )

    return render_template(
        "project_tracker/dashboard.html",
        **context
    )


@projects_bp.route("/projects/create", methods=["GET", "POST"])
@jwt_required()
@admin_required
def create_project():
    if request.method == "POST":
        try:
            project = create_project_from_form(
                request.form,
                current_user
            )

            flash("Project created successfully.", "success")

            return redirect(
                url_for("projects.project_detail", project_id=project.id)
            )

        except (ValueError, PermissionError) as ex:
            flash(str(ex), "error")

    return render_template(
        "project_tracker/create_project.html",
        statuses=PROJECT_STATUSES,
        priorities=PROJECT_PRIORITIES
    )


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@jwt_required()
@admin_required
def edit_project(project_id):
    if request.method == "POST":
        try:
            project = update_project_from_form(
                project_id,
                request.form,
                current_user
            )

            flash("Project updated successfully.", "success")

            return redirect(
                url_for("projects.project_detail", project_id=project.id)
            )

        except ValueError as ex:
            flash(str(ex), "error")

    context = get_project_edit_context(project_id)

    return render_template(
        "project_tracker/edit_project.html",
        **context
    )


@projects_bp.route("/projects/<int:project_id>")
@jwt_required()
def project_detail(project_id):
    if current_user.role == "Exec":
        return redirect(
            url_for("projects.project_report", project_id=project_id)
        )

    try:
        context = get_project_detail_context(project_id, current_user)

    except PermissionError:
        abort(403)

    return render_template(
        "project_tracker/project_detail.html",
        **context
    )


@projects_bp.route("/projects/<int:project_id>/tasks")
@jwt_required()
def task_management(project_id):
    if current_user.role == "Exec":
        return redirect(
            url_for("projects.project_report", project_id=project_id)
        )

    try:
        context = get_task_management_context(project_id, current_user)

    except PermissionError:
        abort(403)

    return render_template(
        "project_tracker/task_management.html",
        **context
    )


@projects_bp.route("/projects/<int:project_id>/tasks/create", methods=["POST"])
@jwt_required()
@admin_required
def create_task(project_id):
    try:
        create_task_from_form(
            project_id,
            request.form,
            user_id=current_user
        )

        flash("Task created successfully.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(
        url_for("projects.task_management", project_id=project_id)
    )


@projects_bp.route("/tasks/<int:task_id>/update", methods=["POST"])
@jwt_required()
def update_task(task_id):
    try:
        task = update_task_from_form(task_id, request.form, current_user)
        flash("Task updated.", "success")

        return redirect(
            url_for("projects.task_management", project_id=task.project_id)
        )

    except PermissionError as ex:
        flash(str(ex), "error")
        return redirect(url_for("projects.dashboard"))


@projects_bp.route("/tasks/<int:task_id>/notes/create", methods=["POST"])
@jwt_required()
def create_task_note(task_id):
    try:
        note = add_task_note(task_id, request.form, current_user)

        flash("Task note added.", "success")

        return redirect(
            url_for("projects.task_management", project_id=note.task.project_id)
        )

    except (PermissionError, ValueError) as ex:
        flash(str(ex), "error")
        return redirect(url_for("projects.dashboard"))


@projects_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@jwt_required()
@admin_required
def remove_task(task_id):
    project_id = delete_task(task_id, user_id=current_user.id)

    flash("Task deleted.", "success")

    return redirect(
        url_for("projects.task_management", project_id=project_id)
    )


@projects_bp.route("/projects/<int:project_id>/report")
@jwt_required()
def project_report(project_id):
    try:
        context = get_project_report_context(project_id, current_user)

    except PermissionError:
        abort(403)

    return render_template(
        "project_tracker/project_report.html",
        **context
    )