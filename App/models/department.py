from datetime import datetime

from App.database import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    users = db.relationship(
        "User",
        back_populates="department",
        lazy=True
    )

    projects = db.relationship(
        "Project",
        back_populates="department",
        lazy=True
    )

    def __repr__(self):
        return f"<Department {self.name}>"