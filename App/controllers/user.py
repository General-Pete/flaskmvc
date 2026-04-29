from App.models import User
from App.database import db


def create_user(username, password):
    username = (username or "").strip()

    if not username:
        raise ValueError("Username is required.")

    if not password:
        raise ValueError("Password is required.")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        raise ValueError("A user with that username already exists.")

    new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user(id):
    return User.query.get(id)


def get_all_users():
    return User.query.order_by(User.username.asc()).all()


def get_all_users_json():
    users = User.query.order_by(User.username.asc()).all()

    if not users:
        return []

    return [user.get_json() for user in users]


def update_user(id, username):
    user = get_user(id)

    if not user:
        return None

    username = (username or "").strip()

    if not username:
        raise ValueError("Username is required.")

    user.username = username

    db.session.add(user)
    db.session.commit()

    return user


def delete_user(id):
    user = get_user(id)

    if not user:
        return None

    db.session.delete(user)
    db.session.commit()

    return user