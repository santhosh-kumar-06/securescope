import uuid
from sqlalchemy.orm import Session
from .. import models


def log_action(db: Session, action: str, details: dict | None = None, actor: str = "system"):
    entry = models.AuditLog(
        id=str(uuid.uuid4()),
        actor=actor,
        action=action,
        details=details or {},
    )
    db.add(entry)
    db.commit()
    return entry
