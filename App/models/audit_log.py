from . import db
from datetime import datetime 

class AuditLog(db.Model):
    __tablename__="audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"),
        nullable=False
    )

    action = db.Column(db.String(20), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer)
    description =db.Column(db.String(255), nullable=False)

    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship("User", backref="audit_logs")