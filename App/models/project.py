from datetime import datetime
from decimal import Decimal

from App.database import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False,
        index=True
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    
    department = db.relationship(
        "Department",
        back_populates="projects"
    )

    
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    project_type = db.Column(db.String(100), nullable=True)
    current_focus = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(50), nullable=False, default="Not Started")
    priority = db.Column(db.String(50), nullable=False, default="Medium")

    budget_amount = db.Column(db.Numeric(14, 2), nullable=True)
    budget_tracker_value = db.Column(db.String(100), nullable=True)

    expected_outcome = db.Column(db.Text, nullable=True)
    other_info = db.Column(db.Text, nullable=True)

    start_date = db.Column(db.Date, nullable=True)
    target_end_date = db.Column(db.Date, nullable=True)

    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    creator= db.relationship(
        "User",
        backref="projects_created"
    )

    tasks = db.relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True
    )

    milestones = db.relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="Milestone.created_at.asc()"
    )

    update_items = db.relationship(
        "ProjectUpdateItem",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ProjectUpdateItem.sort_order"
    )

    outgoing_relationships = db.relationship(
        "ProjectRelationship",
        foreign_keys="ProjectRelationship.source_project_id",
        back_populates="source_project",
        cascade="all, delete-orphan",
        lazy=True
    )

    incoming_relationships = db.relationship(
        "ProjectRelationship",
        foreign_keys="ProjectRelationship.target_project_id",
        back_populates="target_project",
        cascade="all, delete-orphan",
        lazy=True
    )

    @property
    def total_tasks(self):
        return len(self.tasks)

    @property
    def completed_tasks_count(self):
        return len([task for task in self.tasks if task.status == "Completed"])

    @property
    def in_progress_tasks_count(self):
        return len([task for task in self.tasks if task.status == "In Progress"])

    @property
    def todo_tasks_count(self):
        return len([task for task in self.tasks if task.status == "To-Do"])

    @property
    def progress_percent(self):
        if self.total_tasks == 0:
            return 0

        return round((self.completed_tasks_count / self.total_tasks) * 100)

    @property
    def budget_display(self):
        if self.budget_amount is None:
            return "TBD"

        amount = Decimal(self.budget_amount)
        return f"${amount:,.2f}"

    def get_items_by_category(self, category):
        return [
            item for item in self.update_items
            if item.category == category
        ]

    def __repr__(self):
        return f"<Project {self.name}>"