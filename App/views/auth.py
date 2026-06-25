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
from App.database import db
from App.controllers.auth import validate_password_strength 

import secrets

from App.models import User
from App.controllers.email import send_reset_email


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

    login_result = login(username, password)

    if not login_result:
        flash("Bad username or password.", "error")
        return redirect(url_for("auth_views.login_page", next=next_url))

    # Force password change for first login
    if login_result["must_change_password"]:
        response = redirect(url_for("auth_views.change_password"))

        set_access_cookies(
            response,
            login_result["access_token"]
        )

        flash("You must change your password before continuing.", "error")
        return response

    # Normal login
    response = redirect(next_url)

    set_access_cookies(
        response,
        login_result["access_token"]
    )

    flash("Login successful.", "success")

    return response

"""
@auth_views.route("/login", methods=["POST"])
def login_action():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next") or url_for("projects.dashboard")

    login_result = login(username, password)

    if not login_result:
        flash("Bad username or password.", "error")
        return redirect(url_for("auth_views.login_page", next=next_url))
    
    if login_result["must_change_password"]:
        response = redirect(url_for("auth_views.change_password"))

    set_access_cookies(
        response,
        login_result["access_token"]
    )

    flash("You must change your password before continuing.", "error")

    return 

    response = redirect(next_url)

        set_access_cookies(
        response,
        login_result["access_token"]
    )

    flash("Login successful.", "success")

    return response """"""
"""

@auth_views.route("/change-password", methods=["GET", "POST"])
@jwt_required()
def change_password():

    print("CHANGE PASSWORD ROUTE HIT")
    print("METHOD:", request.method)

    if request.method == "POST":

        new_password = request.form.get("password")

        try:
            validate_password_strength(new_password)

        except ValueError as ex:
            flash(str(ex), "error")
            return redirect(
                url_for("auth_views.change_password")
            )

        user = current_user

        user.set_password(new_password)
        user.must_change_password = False

        db.session.commit()

        flash(
            "Password updated successfully.",
            "success"
        )

        return redirect(
            url_for("projects.dashboard")
        )

    return render_template("auth/change_password.html")

@auth_views.route("/logout", methods=["GET"])
def logout_action():
    response = redirect(url_for("auth_views.login_page"))
    unset_jwt_cookies(response)
    flash("Logged out.", "success")

    return response


@auth_views.route("/api/login", methods=["POST"])
def user_login_api():
    data = request.json or {}

    login_result = login(
        data.get("username"),
        data.get("password")
    )

    if not login_result:
        return jsonify(message="Bad username or password."), 401

    response = jsonify(
        access_token=login_result["access_token"],
        must_change_password=login_result["must_change_password"]
    )

    set_access_cookies(
        response,
        login_result["access_token"]
    )

    return response

@auth_views.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        user = User.query.filter_by(email=email).first()

        if user:

            # Generate temporary password
            temp_password = secrets.token_urlsafe(10)

            user.set_password(temp_password)
            user.must_change_password = True

            db.session.commit()

            print("\n" + "=" * 50)
            print("TEMP PASSWORD:", temp_password)
            print("=" * 50 + "\n")

        flash(
            "If the email exists, a reset email has been sent.",
            "success"
        )

        return redirect(url_for("auth_views.login_page"))

    return render_template(
        "auth/forgot_password.html"
    )


"""
@auth_views.route("/api/login", methods=["POST"])
def user_login_api():
    data = request.json or {}

    token = login(data.get("username"), data.get("password"))

    if not token:
        return jsonify(message="Bad username or password."), 401

    response = jsonify(access_token=token)
    set_access_cookies(response, token)

    return response
"""
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