"""add milestones and task milestone assignment

Revision ID: 9ef2e88b80c5
Revises:
Create Date: 2026-05-16 23:56:36.311256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ef2e88b80c5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "milestones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_milestones_project_id_projects"
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_milestones_project_id",
        "milestones",
        ["project_id"],
        unique=False
    )

    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("milestone_id", sa.Integer(), nullable=True)
        )

        batch_op.create_index(
            "ix_tasks_milestone_id",
            ["milestone_id"],
            unique=False
        )

        batch_op.create_foreign_key(
            "fk_tasks_milestone_id_milestones",
            "milestones",
            ["milestone_id"],
            ["id"]
        )


def downgrade():
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_tasks_milestone_id_milestones",
            type_="foreignkey"
        )

        batch_op.drop_index("ix_tasks_milestone_id")

        batch_op.drop_column("milestone_id")

    op.drop_index(
        "ix_milestones_project_id",
        table_name="milestones"
    )

    op.drop_table("milestones")