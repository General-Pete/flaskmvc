from App.database import db
from App.models import AuditLog


def log_audit(
    user_id,
    action,
    module,
    record_id,
    description,
    old_value=None,
    new_value=None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        module=module,
        record_id=record_id,
        description=description,
        old_value=old_value,
        new_value=new_value
    )

    db.session.add(log)
    db.session.commit()