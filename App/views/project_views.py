from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_jwt_extended import jwt_required

from App.controllers.project_controller import (
    PROJECT_STATUSES,
    PROJECT_PRIORITIES,
    TASK_STATUSES,
    get_dashboard_context,
    create_project_from_form,
    get_project_detail_context,
    get_task_management_context,
    create_task_from_form,
    update_task_from_form,
    delete_task,
    get_project_report_context
)


projects_bp = Blueprint(
    "projects",
    __name__,
    template_folder="../templates"
)


@projects_bp.route("/projects")
@jwt_required()
def dashboard():
    context = get_dashboard_context()

    return render_template(
        "project_tracker/dashboard.html",
        **context
    )


@projects_bp.route("/projects/create", methods=["GET", "POST"])
@jwt_required()
def create_project():
    if request.method == "POST":
        try:
            project = create_project_from_form(request.form)
            flash("Project created successfully.", "success")

            return redirect(
                url_for("projects.project_detail", project_id=project.id)
            )

        except ValueError as ex:
            flash(str(ex), "error")

    return render_template(
        "project_tracker/create_project.html",
        statuses=PROJECT_STATUSES,
        priorities=PROJECT_PRIORITIES
    )


@projects_bp.route("/projects/<int:project_id>")
@jwt_required()
def project_detail(project_id):
    context = get_project_detail_context(project_id)

    return render_template(
        "project_tracker/project_detail.html",
        **context
    )


@projects_bp.route("/projects/<int:project_id>/tasks")
@jwt_required()
def task_management(project_id):
    context = get_task_management_context(project_id)

    return render_template(
        "project_tracker/task_management.html",
        **context
    )


@projects_bp.route("/projects/<int:project_id>/tasks/create", methods=["POST"])
@jwt_required()
def create_task(project_id):
    try:
        create_task_from_form(project_id, request.form)
        flash("Task created successfully.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(
        url_for("projects.task_management", project_id=project_id)
    )


@projects_bp.route("/tasks/<int:task_id>/update", methods=["POST"])
@jwt_required()
def update_task(task_id):
    task = update_task_from_form(task_id, request.form)

    flash("Task updated.", "success")

    return redirect(
        url_for("projects.task_management", project_id=task.project_id)
    )


@projects_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@jwt_required()
def remove_task(task_id):
    project_id = delete_task(task_id)

    flash("Task deleted.", "success")

    return redirect(
        url_for("projects.task_management", project_id=project_id)
    )


@projects_bp.route("/projects/<int:project_id>/report")
@jwt_required()
def project_report(project_id):
    context = get_project_report_context(project_id)

    return render_template(
        "project_tracker/project_report.html",
        **context
    )