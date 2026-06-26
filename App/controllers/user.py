from App.models import User, Department
from App.database import db

import secrets
import string


USER_ROLES = [
    "Admin",
    "User",
    "Exec",
    "Head"
]

def generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits

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


def create_user(username, email, password, role="User", department_id=None):
    username = (username or "").strip()
    role = role or "User"
    email = (email or "").strip().lower()

    if role not in USER_ROLES:
        role = "User"

    if not username:
        raise ValueError("Username is required.")
    
    if email:
        existing_email = User.query.filter_by(email=email).first()

    if existing_email:
        raise ValueError("A user with that email already exists.")

    if not password:
        raise ValueError("Password is required.")

    if role != "Exec" and not department_id:
        raise ValueError("Department is required for Admin, Head and User accounts.")

    if role == "Exec":
        department_id = None

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        raise ValueError("A user with that username already exists.")
    
    existing_email = User.query.filter_by(email=email).first()

    new_user = User(
        email=email,
        username=username,
        password=password,
        role=role,
        department_id=department_id,
        must_change_password=True
    )

    db.session.add(new_user)
    db.session.commit()

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


def update_user(id, username=None, email=None, role=None, department_id=None):

    user = get_user(id)

    if not user:
        return None

    # -----------------------------
    # Username
    # -----------------------------
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

    # -----------------------------
    # Department
    # -----------------------------
    if department_id is not None:
        user.department_id = department_id

    if user.role == "Exec":
        user.department_id = None

    elif not user.department_id:
        raise ValueError(
            "Department is required for Admin, Head and User accounts."
        )

    db.session.commit()

    return user


def delete_user(id):
    user = get_user(id)

    if not user:
        return None

    db.session.delete(user)
    db.session.commit()

    return user

def reset_user_password(id):

    user = get_user(id)

    if not user:
        return None

    new_password = generate_temp_password()

    user.set_password(new_password)

    user.must_change_password = True

    db.session.commit()

    return new_password