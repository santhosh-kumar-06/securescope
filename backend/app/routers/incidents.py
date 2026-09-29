import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.correlation_engine import correlate_and_generate_incidents
from ..services.audit import log_action

router = APIRouter(tags=["incidents"])

VALID_STATUSES = {s.value for s in models.IncidentStatus}


@router.post("/api/incidents/correlate", response_model=list[schemas.IncidentOut])
def trigger_correlation(db: Session = Depends(get_db)):
    incidents = correlate_and_generate_incidents(db)
    log_action(db, "incidents.correlated", {"created": [i.incident_code for i in incidents]})
    return [_incident_to_out(i) for i in incidents]


@router.get("/api/incidents", response_model=list[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).order_by(models.Incident.first_observed.asc()).all()
    return [_incident_to_out(i) for i in incidents]


@router.get("/api/incidents/{incident_id}", response_model=schemas.IncidentDetailOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    events = [ie.event for ie in incident.incident_events]
    events.sort(key=lambda e: e.timestamp)
    out = _incident_to_out(incident)
    return schemas.IncidentDetailOut(**out.model_dump(), events=events)


@router.patch("/api/incidents/{incident_id}/status", response_model=schemas.IncidentOut)
def update_incident_status(incident_id: str, payload: schemas.IncidentStatusUpdate, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Status must be one of {sorted(VALID_STATUSES)}")
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    db.commit()
    db.refresh(incident)
    log_action(db, "incident.status_changed", {"incident_code": incident.incident_code, "status": payload.status})
    return _incident_to_out(incident)


@router.post("/api/response-actions", response_model=schemas.ResponseActionOut)
def record_response_action(payload: schemas.ResponseActionIn, db: Session = Depends(get_db)):
    """
    Records a *simulated* recommended response action for the audit trail.
    This endpoint never performs any live containment action — it is a
    training-mode acknowledgement, clearly logged as simulated.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == payload.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    action = models.ResponseAction(
        id=str(uuid.uuid4()),
        incident_id=incident.id,
        action_type=payload.action_type,
        description=payload.description,
        simulated="true",
        performed_at=datetime.utcnow(),
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    log_action(db, "response_action.simulated", {
        "incident_code": incident.incident_code,
        "action_type": payload.action_type,
    })
    return action


def _incident_to_out(incident: models.Incident) -> schemas.IncidentOut:
    return schemas.IncidentOut(
        id=incident.id,
        incident_code=incident.incident_code,
        severity=incident.severity.value if hasattr(incident.severity, "value") else incident.severity,
        affected_identity=incident.affected_identity,
        affected_asset=incident.affected_asset,
        first_observed=incident.first_observed,
        last_observed=incident.last_observed,
        status=incident.status.value if hasattr(incident.status, "value") else incident.status,
        summary=incident.summary,
        event_count=len(incident.incident_events),
    )
