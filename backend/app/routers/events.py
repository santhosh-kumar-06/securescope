import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(tags=["events"])


def _next_event_code(db: Session) -> str:
    count = db.query(models.SecurityEvent).count()
    return f"SEC-{count + 1:05d}"


@router.post("/api/test-events", response_model=schemas.SecurityEventOut)
def create_test_event(payload: schemas.SecurityEventIn, db: Session = Depends(get_db)):
    """Ingest a controlled/demo security event (no live agent required)."""
    event = models.SecurityEvent(
        id=str(uuid.uuid4()),
        event_code=_next_event_code(db),
        timestamp=payload.timestamp or datetime.utcnow(),
        source=payload.source,
        user=payload.user,
        asset=payload.asset,
        event_type=payload.event_type,
        severity=payload.severity or "INFO",
        status="New",
        raw_context=payload.context or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    log_action(db, "event.ingested", {"event_code": event.event_code, "event_type": event.event_type})
    return event


@router.get("/api/events", response_model=list[schemas.SecurityEventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.SecurityEvent).order_by(models.SecurityEvent.timestamp.asc()).all()
