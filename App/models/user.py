from werkzeug.security import check_password_hash, generate_password_hash

from App.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=True)

    # Admin = department admin/manager/director
    # User = normal department user
    # Exec = executive/global viewer
    # Head = Head of Department 
    role = db.Column(db.String(20), nullable=False, default="User")

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=True,
        index=True
    )

    department = db.relationship(
        "Department",
        back_populates="users"
    )

    #Temp Password
    must_change_password = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )
    
    def __init__(self, username, email, password, role="User", department_id=None, must_change_password=False):
        self.username = username
        self.email = email
        self.role = role or "User"
        self.department_id = department_id

        self.set_password(password)
        self.must_change_password = must_change_password

    def get_json(self):
        return {
            "id": self.id,
            "email":self.email,
            "username": self.username,
            "role": self.role,
            "department_id": self.department_id,
            "department": self.department.name if self.department else None
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
    
    @property
    def is_head(self):
        return self.role == "Head"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"