from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)


def get_migrate(app):
    return migrate


def create_db(app):
    with app.app_context():
        from App.models import (
            Department,
            User,
            Project,
            Milestone,
            Task,
            TaskNote,
            ProjectUpdateItem,
            ProjectRelationship,
            ActivityLog
        )

        db.create_all()