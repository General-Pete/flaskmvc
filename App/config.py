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
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = "yourgmail@gmail.com"
    MAIL_PASSWORD = "your_google_app_password"

    MAIL_DEFAULT_SENDER = "yourgmail@gmail.com"    