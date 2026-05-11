import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db").replace("\\", "/")
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_TOKEN_LOCATION = ["cookies", "headers"]
JWT_ACCESS_COOKIE_NAME = "access_token"
JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
JWT_COOKIE_CSRF_PROTECT = False

UPLOADED_PHOTOS_DEST = "App/uploads"
TEMPLATES_AUTO_RELOAD = True

AUTO_CREATE_DB = os.environ.get("AUTO_CREATE_DB", "false").lower() == "true"

FLASK_ADMIN_SWATCH = "darkly"