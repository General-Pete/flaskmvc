from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from App.database import db
from App.models import (
    User,
    Project,
    Task,
    ProjectUpdateItem,
    ProjectRelationship,
    ActivityLog
)


def setup_admin(app):
    admin = Admin(app, name='FlaskMVC')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Project, db.session))
    admin.add_view(ModelView(Task, db.session))
    admin.add_view(ModelView(ProjectUpdateItem, db.session))
    admin.add_view(ModelView(ProjectRelationship, db.session))
    admin.add_view(ModelView(ActivityLog, db.session))