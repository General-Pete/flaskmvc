from App.models import User, Department
from App.database import db
from App.controllers.audit_log import log_audit

import secrets
import string


USER_ROLES = [
    "Admin",
    "User",
    "Exec",
    "Head"
]

def generate_temp_password(length=12):
    alphabet = (
        string.ascii_letters +
        string.digits +
        "!@#$%&*?"
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


def get_all_departments():
    return (
        Department.query
        .filter_by(is_active=True)
        .order_by(Department.name.asc())
        .all()
    )


def create_department(name, description=None):
    name = (name or "").strip()

    if not name:
        raise ValueError("Department name is required.")

    existing = Department.query.filter_by(name=name).first()

    if existing:
        raise ValueError("Department already exists.")

    department = Department(
        name=name,
        description=(description or "").strip() or None
    )

    db.session.add(department)
    db.session.commit()

    return department


def create_user(username, email, password, role="User", department_id=None, performed_by=None):

    username = (username or "").strip()
    email = (email or "").strip().lower()
    role = role or "User"

    if role not in USER_ROLES:
        role = "User"

    if not username:
        raise ValueError("Username is required.")

    if not password:
        raise ValueError("Password is required.")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        raise ValueError("A user with that username already exists.")

    existing_email = None

    if email:
        existing_email = User.query.filter_by(email=email).first()

    if existing_email:
        raise ValueError("A user with that email already exists.")

    if role != "Exec" and not department_id:
        raise ValueError(
            "Department is required for Admin, Head and User accounts."
        )

    if role == "Exec":
        department_id = None

    new_user = User(
        username=username,
        email=email,
        password=password,
        role=role,
        department_id=department_id,
        must_change_password=True
    )

    db.session.add(new_user)
    db.session.commit()

    log_audit(
        user_id=performed_by,
        action="CREATE",
        module="Users",
        record_id=new_user.id,
            description=f"Created user '{new_user.username}'"  
            )

    return new_user

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user(id):
    return User.query.get(id)


def get_all_users():
    return User.query.order_by(User.username.asc()).all()


def get_users_for_department(department_id):
    return (
        User.query
        .filter(User.department_id == department_id)
        .order_by(User.username.asc())
        .all()
    )


def get_all_users_json():
    users = User.query.order_by(User.username.asc()).all()
    return [user.get_json() for user in users]


def update_user(id, username=None, email=None, role=None, department_id=None, performed_by=None):

    user = get_user(id)

    if not user:
        return None

  
    # Username
   
    if username is not None:

        username = username.strip()

        if username == "":
            raise ValueError("Username is required.")

        existing = User.query.filter_by(username=username).first()

        if existing and existing.id != user.id:
            raise ValueError("Username already exists.")

        user.username = username

   

    if email is not None:

        email = email.strip().lower()

    if email != "":

        existing = User.query.filter_by(email=email).first()

        if existing and existing.id != user.id:
            raise ValueError("Email already exists.")

        user.email = email

   
    if role is not None:

        if role not in USER_ROLES:
            raise ValueError("Invalid role.")

        user.role = role

    # Department
  
    if department_id is not None:
        user.department_id = department_id

    if user.role == "Exec":
        user.department_id = None

    elif not user.department_id:
        raise ValueError(
            "Department is required for Admin, Head and User accounts."
        )

    db.session.commit()

    log_audit(
        user_id=performed_by,
        action="UPDATE",
        module="Users",
        record_id=user.id,
            description=f"Update user '{user.username}'"
                    )

    return user


def delete_user(id, performed_by=None):
    user = get_user(id)

    if not user:
        return None
    

    log_audit(
        user_id=performed_by,
        action="DELETE",
        module="Users",
        record_id=user.id,
            description=f"Delete user '{user.username}'"
    )

    db.session.delete(user)
    db.session.commit()

    return user

def reset_user_password(id):

    user = get_user(id)

    if not user:
        return None

    temporary_password = generate_temp_password()

    user.reset_password(temporary_password)

    db.session.commit()

    return temporary_password