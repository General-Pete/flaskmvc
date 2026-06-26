import os


def load_config(app, overrides):
    if os.path.exists(os.path.join("./App", "custom_config.py")):
        app.config.from_object("App.custom_config")
    else:
        app.config.from_object("App.default_config")

    # Allows environment variables prefixed with FLASK_ to override config
    app.config.from_prefixed_env()

    # Safe shared defaults
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["UPLOADED_PHOTOS_DEST"] = "App/uploads"

    # Apply manual overrides passed to create_app()
    for key in overrides:
        app.config[key] = overrides[key]

    #Email
    app.config["MAIL_SERVER"] = "smtp.office365.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True

    app.config["MAIL_USERNAME"] = "yourname@mhs.gov.tt"
    app.config["MAIL_PASSWORD"] = "your_password_or_app_password"

    app.config["MAIL_DEFAULT_SENDER"] = "yourname@mhs.gov.tt"