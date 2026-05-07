import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "sqlite:///instance/app.db"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_TOKEN_LOCATION = ["cookies", "headers"]
JWT_ACCESS_COOKIE_NAME = "access_token"

# false locally, true when HTTPS is working
JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
JWT_COOKIE_CSRF_PROTECT = False

UPLOADED_PHOTOS_DEST = "App/uploads"
TEMPLATES_AUTO_RELOAD = True