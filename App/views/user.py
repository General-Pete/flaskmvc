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

from flask_jwt_extended import jwt_required

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    delete_user
)


user_views = Blueprint(
    "user_views",
    __name__,
    template_folder="../templates"
)


@user_views.route("/people", methods=["GET"])
@jwt_required()
def get_people_page():
    users = get_all_users()

    return render_template(
        "users.html",
        users=users
    )


@user_views.route("/people", methods=["POST"])
@jwt_required()
def create_person_action():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    try:
        create_user(username, password)
        flash(f"Person {username} created.", "success")

    except ValueError as ex:
        flash(str(ex), "error")

    return redirect(url_for("user_views.get_people_page"))


@user_views.route("/people/<int:user_id>/delete", methods=["POST"])
@jwt_required()
def delete_person_action(user_id):
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


# Backward compatible route if your old navbar still points to /users
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
    data = request.json or {}

    try:
        user = create_user(data.get("username"), data.get("password"))

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