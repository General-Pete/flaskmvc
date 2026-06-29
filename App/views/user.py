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
    get_users_for_department,
    get_user,
    update_user,
    delete_user,
    USER_ROLES
)
from App.controllers.user import get_all_departments
from App.controllers.user import reset_user_password 


user_views = Blueprint(
    "user_views",
    __name__,
    template_folder="../templates"
)

@user_views.route(
    "/people/<int:user_id>/reset-password",
    methods=["GET"]
)
@jwt_required()
def reset_password_action(user_id):

    new_password = reset_user_password(user_id)

    if new_password is None:
        flash("User not found.", "danger")
        return redirect(url_for("user_views.get_people_page"))

    flash(
        f"Temporary password: {new_password}",
        "success"
    )

    return redirect(
        url_for("user_views.get_people_page")
    )

def require_management():
    if not current_user or current_user.role not in ["Admin","Head"]:
        flash("Admins and Heads only.", "error")
        return False

    return True

@user_views.route("/people", methods=["GET"])
@jwt_required()
def get_people_page():

    if not require_management():
        return redirect(url_for("projects.dashboard"))

    search = request.args.get("search", "").strip().lower()

    if current_user.role == "Head":
        users = get_users_for_department(current_user.department_id)
    else:
        users = get_all_users()

    if search:
        users = [
            user for user in users
            if (
                search in (user.username or "").lower()
                or search in (user.role or "").lower()
                or search in ((user.department.name if user.department else "")).lower()
            )
    ]

    return render_template(
        "users.html",
        users=users,
        roles=USER_ROLES,
        departments=get_all_departments(),
        search=search
    )




@user_views.route("/people", methods=["POST"])
@jwt_required()
def create_person_action():
    if not require_management():
        return redirect(url_for("projects.dashboard"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "User")
    department_id_raw = request.form.get("department_id")
    department_id = int(department_id_raw) if department_id_raw else None

    if current_user.role == "Head":
        department_id = current_user.department_id 

    try:
        create_user(username, email, password, role, department_id)
        flash(f"Person {username} created.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/people/<int:user_id>/role", methods=["POST"])
@jwt_required()
def update_person_role_action(user_id):

    if not require_management():
        return redirect(url_for("projects.dashboard"))

    user = get_user(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_views.get_people_page"))

    if current_user.role == "Head":
        if user.department_id != current_user.department_id:
            flash("You can only manage users in your department.", "error")
            return redirect(url_for("user_views.get_people_page"))

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

    if not require_management():
        return redirect(url_for("projects.dashboard"))

    user = get_user(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_views.get_people_page"))

    if current_user.role == "Head":
        if user.department_id != current_user.department_id:
            flash("You can only manage users in your department.", "error")
            return redirect(url_for("user_views.get_people_page"))

    try:
        delete_user(user_id)
        flash("Person deleted.", "success")

    except Exception:
        flash(
            "This person could not be deleted. They may already be assigned to tasks.",
            "error"
        )

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/people/<int:user_id>/edit", methods=["POST"])
@jwt_required()
def edit_person_action(user_id):

    if not require_management():
        return redirect(url_for("user_views.get_people_page"))

    user = get_user(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_views.get_people_page"))

    # Heads can only edit users in their department
    if current_user.role == "Head":
        if user.department_id != current_user.department_id:
            flash("You can only edit users in your department.", "error")
            return redirect(url_for("user_views.get_people_page"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "User")

    department_id = request.form.get("department_id")

    if department_id:
        department_id = int(department_id)
    else:
        department_id = None

    # Heads cannot move users to another department
    if current_user.role == "Head":
        department_id = current_user.department_id

    try:

        update_user(
            user_id,
            username=username,
            email=email,
            role=role,
            department_id=department_id
        )

        flash("User updated successfully.", "success")

    except ValueError as ex:

        flash(str(ex), "error")

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
    if not require_management():
        return jsonify(message="Admins only."), 403

    data = request.json or {}

    try:
        user = create_user(
            data.get("username"),
            data.get("email"),
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