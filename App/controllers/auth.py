from flask_jwt_extended import (
    create_access_token,
    JWTManager,
    get_jwt_identity,
    verify_jwt_in_request
)

from App.models import User


def login(username, password):
    user = User.query.filter_by(username=username).first()

    if not user: 
        return None;

    if not user.check_password(password):
        return None
    
    #Blocks Access if Temp Password is still active.
    if user.must_change_password:
        return{
            "access_token":create_access_token(identity=str(user.id)),
            "must_change_password": True

        } 
    
    return{
            "access_token": create_access_token(identity=str(user.id)),
            "must_change_password":False

        }

    #if user.must_change_password:

        #if user and user.check_password(password):
           # return create_access_token(identity=str(user.id))

    #return None


def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        return str(identity)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]

        try:
            return User.query.get(int(identity))
        except Exception:
            return None

    return jwt


def add_auth_context(app):
    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()

            if user_id:
                current_user = User.query.get(int(user_id))
                is_authenticated = current_user is not None
            else:
                current_user = None
                is_authenticated = False

        except Exception:
            current_user = None
            is_authenticated = False

        return dict(
            is_authenticated=is_authenticated,
            current_user=current_user
        )