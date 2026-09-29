"""
Rule-based defensive detection engine.

Deliberately simple if/else rules (no ML) operating over recent
SecurityEvent rows. Each rule returns a structured detection with a
rule id, reason, evidence, severity, and recommended action so the
frontend/audit trail can show exactly why something fired.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional

from ..models import SecurityEvent, Severity


@dataclass
class Detection:
    rule_id: str
    reason: str
    evidence: List[str]
    severity: str
    recommended_action: str
    event_ids: List[str] = field(default_factory=list)


RECOVERY_CODE_EVENT_TYPES = {"recovery-code usage", "authentication anomaly"}
SENSITIVE_ACCESS_EVENT_TYPES = {"sensitive resource access", "account activity"}
TRANSFER_EVENT_TYPES = {"suspicious outbound transfer", "unusual destination"}
MOVEMENT_EVENT_TYPES = {"potential lateral movement indicator", "configuration change", "endpoint event"}


def _norm(event_type: str) -> str:
    return (event_type or "").strip().lower()


def rule_1_recovery_code_anomaly(events: List[SecurityEvent]) -> List[Detection]:
    out = []
    for e in events:
        if _norm(e.event_type) in RECOVERY_CODE_EVENT_TYPES:
            out.append(Detection(
                rule_id="RULE-1",
                reason="Recovery-code / authentication event observed from an unusual context.",
                evidence=[f"Event {e.event_code}: {e.event_type} by {e.user or 'unknown user'} from {e.source}"],
                severity=Severity.HIGH.value,
                recommended_action="Verify identity through an independent channel; consider forcing a credential reset.",
                event_ids=[e.id],
            ))
    return out


def rule_2_sensitive_access_after_auth(events: List[SecurityEvent]) -> List[Detection]:
    out = []
    sorted_events = sorted(events, key=lambda e: e.timestamp)
    auth_events = [e for e in sorted_events if _norm(e.event_type) in RECOVERY_CODE_EVENT_TYPES]
    for auth in auth_events:
        for e in sorted_events:
            if (_norm(e.event_type) in SENSITIVE_ACCESS_EVENT_TYPES
                    and e.timestamp >= auth.timestamp
                    and e.timestamp <= auth.timestamp + timedelta(hours=6)):
                out.append(Detection(
                    rule_id="RULE-2",
                    reason="Sensitive-resource access followed suspicious authentication.",
                    evidence=[
                        f"Auth event {auth.event_code} at {auth.timestamp.isoformat()}",
                        f"Access event {e.event_code} at {e.timestamp.isoformat()}",
                    ],
                    severity=Severity.HIGH.value,
                    recommended_action="Escalate incident severity; review scope of accessed records.",
                    event_ids=[auth.id, e.id],
                ))
    return out


def rule_3_transfer_anomaly(events: List[SecurityEvent]) -> List[Detection]:
    out = []
    for e in events:
        if _norm(e.event_type) in TRANSFER_EVENT_TYPES:
            out.append(Detection(
                rule_id="RULE-3",
                reason="Outbound transfer volume or destination is significantly abnormal.",
                evidence=[f"Event {e.event_code}: {e.event_type} involving asset {e.asset or 'unknown'}"],
                severity=Severity.CRITICAL.value,
                recommended_action="Investigate destination; contain affected identity/host if warranted.",
                event_ids=[e.id],
            ))
    return out


def rule_4_full_chain_correlation(events: List[SecurityEvent]) -> List[Detection]:
    types_seen = {_norm(e.event_type) for e in events}
    has_auth = bool(types_seen & RECOVERY_CODE_EVENT_TYPES)
    has_access = bool(types_seen & SENSITIVE_ACCESS_EVENT_TYPES)
    has_transfer = bool(types_seen & TRANSFER_EVENT_TYPES)
    if has_auth and has_access and has_transfer:
        relevant = [e for e in events if _norm(e.event_type) in (
            RECOVERY_CODE_EVENT_TYPES | SENSITIVE_ACCESS_EVENT_TYPES | TRANSFER_EVENT_TYPES | MOVEMENT_EVENT_TYPES
        )]
        return [Detection(
            rule_id="RULE-4",
            reason="Suspicious authentication, sensitive-resource access, and unusual transfer occurred together.",
            evidence=[f"{e.event_code}: {e.event_type}" for e in sorted(relevant, key=lambda x: x.timestamp)],
            severity=Severity.CRITICAL.value,
            recommended_action="Open a correlated incident; begin containment and evidence preservation immediately.",
            event_ids=[e.id for e in relevant],
        )]
    return []


def run_detections(events: List[SecurityEvent]) -> List[Detection]:
    detections: List[Detection] = []
    detections += rule_1_recovery_code_anomaly(events)
    detections += rule_2_sensitive_access_after_auth(events)
    detections += rule_3_transfer_anomaly(events)
    detections += rule_4_full_chain_correlation(events)
    return detections
