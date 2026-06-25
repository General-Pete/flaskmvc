from flask_mail import Message
from flask import current_app


def send_reset_email(email, temp_password):

    msg = Message(
        subject="Project Tracker Password Reset",
        recipients=[email]
    )

    msg.body = f"""
Your password has been reset.

Temporary Password:
{temp_password}

You will be required to change it when you log in.

AUT Project Tracker
"""

    current_app.extensions["mail"].send(msg)