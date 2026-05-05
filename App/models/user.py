from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    # Roles:
    # Admin = full control
    # User = assigned task user
    # Exec = dashboard/report only
    role = db.Column(db.String(20), nullable=False, default="User")

    def __init__(self, username, password, role="User"):
        self.username = username
        self.role = role or "User"
        self.set_password(password)

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.role == "Admin"

    @property
    def is_exec(self):
        return self.role == "Exec"

    @property
    def is_normal_user(self):
        return self.role == "User"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"