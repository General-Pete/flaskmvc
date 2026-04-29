from datetime import date

from App.database import db
from App.models import (
    User,
    Project,
    Task,
    ProjectUpdateItem,
    ActivityLog
)


def initialize_db():
    db.create_all()


def seed_project_tracker_data():
    """
    Creates sample project dashboard data based on the Figma screens.
    Safe to run once. It will not duplicate if projects already exist.
    """

    if Project.query.first():
        print("Project data already exists. Seed skipped.")
        return

    michelle = User.query.filter_by(username="michelle").first()
    aisha = User.query.filter_by(username="aisha").first()

    if not michelle:
        michelle = User("michelle", "password")
        db.session.add(michelle)

    if not aisha:
        aisha = User("aisha", "password")
        db.session.add(aisha)

    db.session.flush()

    project = Project(
        name="Emergency Communication Infrastructure Upgrade",
        description=(
            "Modernize the E999/990 communications environment by stabilizing "
            "critical sites, upgrading the command centre backbone, and moving "
            "priority infrastructure toward Motorola P25 capability."
        ),
        project_type="Project",
        current_focus="Assessment, design, and phased modernization",
        status="In Progress",
        priority="High",
        budget_amount=10000000,
        budget_tracker_value="Tracker value",
        expected_outcome=(
            "Improve all Emergency communication systems throughout Trinidad "
            "and Tobago."
        ),
        other_info=(
            "Command centre core, gateway, consoles, training, tower readiness, "
            "and migration planning."
        )
    )

    db.session.add(project)
    db.session.flush()

    update_items = [
        ProjectUpdateItem(
            project_id=project.id,
            category="Completed",
            text="Project direction and phased approach established",
            sort_order=1
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Completed",
            text="Priority site stabilization activities identified",
            sort_order=2
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Completed",
            text="RFP to repair San Pedro tower noted as done in tracker",
            sort_order=3
        ),

        ProjectUpdateItem(
            project_id=project.id,
            category="In Progress",
            text="Technical assessment across all 11 sites",
            sort_order=1
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="In Progress",
            text="Asset and microwave transport validation",
            sort_order=2
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="In Progress",
            text="Final network design, BOQ, and migration roadmap",
            sort_order=3
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="In Progress",
            text="Planning for command centre core, gateway, consoles, and training",
            sort_order=4
        ),

        ProjectUpdateItem(
            project_id=project.id,
            category="Risk",
            text="Multi-phase project with significant procurement dependency",
            sort_order=1
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Risk",
            text="Site condition and tower readiness may affect schedule",
            sort_order=2
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Risk",
            text="Command centre upgrade scope likely requires coordinated approvals",
            sort_order=3
        ),

        ProjectUpdateItem(
            project_id=project.id,
            category="Next Step",
            text="Complete the nationwide technical assessment",
            sort_order=1
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Next Step",
            text="Confirm priority sites and urgent remediation works",
            sort_order=2
        ),
        ProjectUpdateItem(
            project_id=project.id,
            category="Next Step",
            text="Finalize scope, BOQ, and procurement package for Phase 2",
            sort_order=3
        ),
    ]

    db.session.add_all(update_items)

    tasks = [
        Task(
            project_id=project.id,
            title="Complete nationwide technical assessment",
            description="Assess the condition and readiness of all emergency communication sites.",
            status="Completed",
            priority="High",
            assigned_user_id=michelle.id,
            due_date=date(2026, 5, 15)
        ),
        Task(
            project_id=project.id,
            title="Validate microwave transport assets",
            description="Confirm transport links, tower readiness, and equipment condition.",
            status="In Progress",
            priority="High",
            assigned_user_id=aisha.id,
            due_date=date(2026, 5, 30)
        ),
        Task(
            project_id=project.id,
            title="Prepare Phase 2 procurement package",
            description="Finalize BOQ, implementation roadmap, and procurement documentation.",
            status="To-Do",
            priority="High",
            assigned_user_id=michelle.id,
            due_date=date(2026, 6, 15)
        )
    ]

    db.session.add_all(tasks)

    log = ActivityLog(
        user_id=None,
        entity_type="Project",
        entity_id=project.id,
        action="Seed Created",
        details="Initial project tracker sample data created."
    )

    db.session.add(log)

    db.session.commit()

    print("Project tracker sample data seeded successfully.")