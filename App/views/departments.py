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
        "departments/add_department.html"
    )