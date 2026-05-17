from datetime import datetime

from App.database import db


class Milestone(db.Model):
    __tablename__ = "milestones"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    target_date = db.Column(db.Date, nullable=True)

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
        back_populates="milestones"
    )

    tasks = db.relationship(
        "Task",
        back_populates="milestone",
        lazy=True
    )

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks_count(self):
        return len([
            task for task in self.tasks
            if task.status == "Completed"
        ])

    @property
    def in_progress_tasks_count(self):
        return len([
            task for task in self.tasks
            if task.status == "In Progress"
        ])

    @property
    def todo_tasks_count(self):
        return len([
            task for task in self.tasks
            if task.status == "To-Do"
        ])

    @property
    def progress_percent(self):
        if self.total_tasks == 0:
            return 0

        return round(
            (self.completed_tasks_count / self.total_tasks) * 100
        )

    @property
    def is_completed(self):
        return (
            self.total_tasks > 0
            and self.completed_tasks_count == self.total_tasks
        )

    @property
    def status_label(self):
        if self.total_tasks == 0:
            return "No Tasks"

        if self.is_completed:
            return "Completed"

        if self.in_progress_tasks_count > 0 or self.completed_tasks_count > 0:
            return "In Progress"

        return "Not Started"

    def __repr__(self):
        return f"<Milestone {self.title}>"