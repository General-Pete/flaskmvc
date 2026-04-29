from datetime import datetime

from App.database import db


class ProjectRelationship(db.Model):
    """
    Handles:

    - Related Projects
    - Depends On
    """

    __tablename__ = "project_relationships"

    id = db.Column(db.Integer, primary_key=True)

    source_project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    target_project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    relationship_type = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    source_project = db.relationship(
        "Project",
        foreign_keys=[source_project_id],
        back_populates="outgoing_relationships"
    )

    target_project = db.relationship(
        "Project",
        foreign_keys=[target_project_id],
        back_populates="incoming_relationships"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "source_project_id",
            "target_project_id",
            "relationship_type",
            name="uq_project_relationship"
        ),
    )

    def __repr__(self):
        return (
            f"<ProjectRelationship "
            f"{self.source_project_id} -> {self.target_project_id} "
            f"({self.relationship_type})>"
        )