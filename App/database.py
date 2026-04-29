from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)


def create_db(app):
    with app.app_context():
        from App.models import (
            User,
            Project,
            Task,
            ProjectUpdateItem,
            ProjectRelationship,
            ActivityLog
        )

        db.create_all()