# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .admin import setup_admin
from App.views.project_views import projects_bp
from .departments import department_views
from flask import Flask 
from flask_mail import Mail 


views = [user_views, index_views, auth_views, projects_bp, department_views] 
# blueprints must be added to this list

mail = Mail()