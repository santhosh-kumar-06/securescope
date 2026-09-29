import uuid
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from .. import models
from .detection_engine import Detection, run_detections


def _next_incident_code(db: Session) -> str:
    count = db.query(models.Incident).count()
    return f"INC-{count + 1:05d}"


def correlate_and_generate_incidents(db: Session) -> List[models.Incident]:
    """
    Pulls all security events, runs the detection engine, and folds the
    resulting detections into a single correlated incident when a full
    attack chain (RULE-4) is present — otherwise records standalone
    high-severity detections as their own incidents.
    """
    events = db.query(models.SecurityEvent).all()
    if not events:
        return []

    detections = run_detections(events)
    if not detections:
        return []

    created_incidents: List[models.Incident] = []

    # Prefer the full-chain correlation (RULE-4) as the canonical incident.
    chain_detections = [d for d in detections if d.rule_id == "RULE-4"]
    other_detections = [d for d in detections if d.rule_id != "RULE-4"]

    def _make_incident(dets: List[Detection], severity: str) -> models.Incident:
        involved_event_ids = sorted({eid for d in dets for eid in d.event_ids})
        involved_events = [e for e in events if e.id in involved_event_ids]
        involved_events.sort(key=lambda e: e.timestamp)

        affected_identity = next((e.user for e in involved_events if e.user), None)
        affected_asset = next((e.asset for e in involved_events if e.asset), None)

        incident = models.Incident(
            id=str(uuid.uuid4()),
            incident_code=_next_incident_code(db),
            severity=severity,
            affected_identity=affected_identity,
            affected_asset=affected_asset,
            first_observed=involved_events[0].timestamp if involved_events else datetime.utcnow(),
            last_observed=involved_events[-1].timestamp if involved_events else datetime.utcnow(),
            status=models.IncidentStatus.INVESTIGATING,
            summary="; ".join(sorted({d.reason for d in dets})),
        )
        db.add(incident)
        db.flush()

        for d in dets:
            for eid in d.event_ids:
                db.add(models.IncidentEvent(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    event_id=eid,
                    rule_id=d.rule_id,
                    rule_reason=d.reason,
                ))
        return incident

    # Avoid duplicating an incident if one already exists for this exact event set.
    existing_event_sets = {
        frozenset(ie.event_id for ie in inc.incident_events)
        for inc in db.query(models.Incident).all()
    }

    if chain_detections:
        event_set = frozenset(eid for d in chain_detections for eid in d.event_ids)
        if event_set not in existing_event_sets:
            created_incidents.append(_make_incident(chain_detections, models.Severity.CRITICAL.value))
    else:
        for d in other_detections:
            event_set = frozenset(d.event_ids)
            if event_set and event_set not in existing_event_sets:
                created_incidents.append(_make_incident([d], d.severity))
                existing_event_sets.add(event_set)

    db.commit()
    for inc in created_incidents:
        db.refresh(inc)
    return created_incidents
