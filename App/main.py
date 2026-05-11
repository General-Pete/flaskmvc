from flask import Flask, render_template, redirect, url_for, request, flash
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from flask_jwt_extended import unset_jwt_cookies
from werkzeug.middleware.proxy_fix import ProxyFix

from App.database import init_db, create_db
from App.config import load_config

from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin


def add_views(app):
    for view in views:
        app.register_blueprint(view)


def create_app(overrides={}):
    app = Flask(__name__, static_url_path="/static")

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

    load_config(app, overrides)

    CORS(app)

    add_auth_context(app)

    photos = UploadSet("photos", TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)

    init_db(app)

    add_views(app)

    jwt = setup_jwt(app)

    setup_admin(app)

    if app.config.get("AUTO_CREATE_DB", False):
        create_db(app)

    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return redirect(
            url_for("auth_views.login_page", next=request.path)
        )

    @jwt.invalid_token_loader
    def custom_invalid_token_response(error):
        response = redirect(
            url_for("auth_views.login_page", next=request.path)
        )

        unset_jwt_cookies(response)
        flash("Please log in again.", "error")

        return response

    return app