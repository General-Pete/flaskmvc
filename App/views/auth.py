from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for
)

from flask_jwt_extended import (
    jwt_required,
    current_user,
    unset_jwt_cookies,
    set_access_cookies
)

from App.controllers import login


auth_views = Blueprint(
    "auth_views",
    __name__,
    template_folder="../templates"
)


@auth_views.route("/login", methods=["GET"])
def login_page():
    next_url = request.args.get("next") or url_for("projects.dashboard")

    return render_template(
        "auth/login.html",
        next_url=next_url
    )


@auth_views.route("/login", methods=["POST"])
def login_action():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next") or url_for("projects.dashboard")

    token = login(username, password)

    if not token:
        flash("Bad username or password.", "error")
        return redirect(url_for("auth_views.login_page", next=next_url))

    response = redirect(next_url)
    set_access_cookies(response, token)

    flash("Login successful.", "success")

    return response


@auth_views.route("/logout", methods=["GET"])
def logout_action():
    response = redirect(url_for("auth_views.login_page"))
    unset_jwt_cookies(response)
    flash("Logged out.", "success")

    return response


@auth_views.route("/api/login", methods=["POST"])
def user_login_api():
    data = request.json or {}

    token = login(data.get("username"), data.get("password"))

    if not token:
        return jsonify(message="Bad username or password."), 401

    response = jsonify(access_token=token)
    set_access_cookies(response, token)

    return response


@auth_views.route("/api/identify", methods=["GET"])
@jwt_required()
def identify_user():
    return jsonify({
        "message": f"username: {current_user.username}, id: {current_user.id}"
    })


@auth_views.route("/api/logout", methods=["GET"])
def logout_api():
    response = jsonify(message="Logged out.")
    unset_jwt_cookies(response)

    return response