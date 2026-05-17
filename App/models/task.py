from datetime import datetime, date

from App.database import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    milestone_id = db.Column(
        db.Integer,
        db.ForeignKey("milestones.id"),
        nullable=True,
        index=True
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), nullable=False, default="To-Do")
    priority = db.Column(db.String(50), nullable=False, default="Medium")

    assigned_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    due_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    project = db.relationship(
        "Project",
        back_populates="tasks"
    )

    milestone = db.relationship(
        "Milestone",
        back_populates="tasks"
    )

    assigned_user = db.relationship(
        "User",
        backref="assigned_project_tasks"
    )

    notes = db.relationship(
        "TaskNote",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="TaskNote.created_at.desc()"
    )

    def is_overdue(self):
        if not self.due_date:
            return False

        return self.status != "Completed" and self.due_date < date.today()

    def __repr__(self):
        return f"<Task {self.title}>"