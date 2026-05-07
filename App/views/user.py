from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    send_from_directory,
    flash,
    redirect,
    url_for
)

from flask_jwt_extended import jwt_required, current_user

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    update_user,
    delete_user,
    USER_ROLES
)
from App.controllers.user import get_all_departments


user_views = Blueprint(
    "user_views",
    __name__,
    template_folder="../templates"
)


def require_admin():
    if not current_user or current_user.role != "Admin":
        flash("Admins only.", "error")
        return False

    return True


@user_views.route("/people", methods=["GET"])
@jwt_required()
def get_people_page():
    if not require_admin():
        return redirect(url_for("projects.dashboard"))

    users = get_all_users()

    return render_template(
        "users.html",
        users=users,
        roles=USER_ROLES,
        departments=get_all_departments()
    )


@user_views.route("/people", methods=["POST"])
@jwt_required()
def create_person_action():
    if not require_admin():
        return redirect(url_for("projects.dashboard"))

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "User")
    department_id_raw = request.form.get("department_id")
    department_id = int(department_id_raw) if department_id_raw else None

    try:
        create_user(username, password, role, department_id)
        flash(f"Person {username} created.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/people/<int:user_id>/role", methods=["POST"])
@jwt_required()
def update_person_role_action(user_id):
    if not require_admin():
        return redirect(url_for("projects.dashboard"))

    role = request.form.get("role", "User")

    try:
        update_user(user_id, role=role)
        flash("Role updated.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/people/<int:user_id>/delete", methods=["POST"])
@jwt_required()
def delete_person_action(user_id):
    if not require_admin():
        return redirect(url_for("projects.dashboard"))

    try:
        deleted_user = delete_user(user_id)

        if deleted_user:
            flash("Person deleted.", "success")
        else:
            flash("Person not found.", "error")

    except Exception:
        flash(
            "This person could not be deleted. They may already be assigned to tasks.",
            "error"
        )

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/users", methods=["GET"])
@jwt_required()
def get_user_page():
    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/users", methods=["POST"])
@jwt_required()
def create_user_action():
    return create_person_action()


@user_views.route("/api/users", methods=["GET"])
@jwt_required()
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)


@user_views.route("/api/users", methods=["POST"])
@jwt_required()
def create_user_endpoint():
    if not require_admin():
        return jsonify(message="Admins only."), 403

    data = request.json or {}

    try:
        user = create_user(
            data.get("username"),
            data.get("password"),
            data.get("role", "User")
        )

        return jsonify({
            "message": f"user {user.username} created with id {user.id}"
        })

    except ValueError as ex:
        return jsonify({
            "message": str(ex)
        }), 400


@user_views.route("/static/users", methods=["GET"])
def static_user_page():
    return send_from_directory("static", "static-user.html")