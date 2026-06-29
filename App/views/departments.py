from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_jwt_extended import jwt_required, current_user

from App.database import db
from App.models import Department

department_views = Blueprint(
    "department_views",
    __name__,
    template_folder="../templates"
)

@department_views.route("/departments/add", methods=["GET", "POST"])
@jwt_required()
def add_department():

    if not current_user.is_admin:
        flash("Access denied.", "error")
        return redirect(url_for("projects.dashboard"))

    if request.method == "POST":

        department_name = request.form.get("name", "").strip()

        if not department_name:
            flash("Department name is required.", "error")
            return redirect(url_for("department_views.add_department"))

        existing = Department.query.filter_by(
            name=department_name
        ).first()

        if existing:
            flash("Department already exists.", "error")
            return redirect(url_for("department_views.add_department"))

        department = Department(
            name=department_name
        )

        db.session.add(department)
        db.session.commit()

        flash("Department created successfully.", "success")

        return redirect(url_for("department_views.list_departments"))

    return render_template(
        "project_tracker/add_department.html",
        departments=Department.query.order_by(
            Department.name.asc()
        ).all()
    )


@department_views.route("/departments/<int:department_id>/delete", methods=["POST"])
@jwt_required()
def delete_department(department_id):

    department = Department.query.get_or_404(department_id)

    if department.users:
        flash(
            "Cannot delete department because users are assigned to it.",
            "error"
        )
        return redirect(url_for("department_views.add_department"))

    if department.projects:
        flash(
            "Cannot delete department because projects are assigned to it.",
            "error"
        )
        return redirect(url_for("department_views.add_department"))

    db.session.delete(department)
    db.session.commit()

    flash("Department deleted successfully.", "success")

    return redirect(url_for("department_views.add_department"))

@department_views.route("/departments", methods=["GET"])
@jwt_required()
def list_departments():

    search = request.args.get("search", "").strip()

    query = Department.query

    if search:
        query = query.filter(
            Department.name.ilike(f"%{search}%")
        )

    departments = query.order_by(Department.name.asc()).all()

    return render_template(
        "project_tracker/add_department.html",
        departments=departments,
        search=search
    )

@department_views.route("/departments/<int:department_id>/edit", methods=["POST"])
@jwt_required()
def edit_department(department_id):

    department = Department.query.get_or_404(department_id)

    department.name = request.form["name"]

    db.session.commit()

    flash("Department updated successfully.", "success")

    return redirect(url_for("department_views.list_departments"))