from datetime import datetime

from App.database import db


class ProjectUpdateItem(db.Model):
    """
    Stores the dashboard bullet-point sections:

    - Completed / Established
    - Currently in Progress
    - Risks / Issues
    - Recommended Next Steps
    """

    __tablename__ = "project_update_items"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    category = db.Column(db.String(50), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    project = db.relationship(
        "Project",
        back_populates="update_items"
    )

    def __repr__(self):
        return f"<ProjectUpdateItem {self.category}: {self.text[:30]}>"