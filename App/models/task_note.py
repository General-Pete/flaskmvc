from datetime import datetime

from App.database import db


class TaskNote(db.Model):
    __tablename__ = "task_notes"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    note = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    task = db.relationship(
        "Task",
        back_populates="notes"
    )

    user = db.relationship(
        "User",
        backref="task_notes"
    )

    def __repr__(self):
        return f"<TaskNote Task={self.task_id} User={self.user_id}>"