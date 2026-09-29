from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, field_validator
import re

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*$"
)
IPV4_RE = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$"
)


class ScanCreateRequest(BaseModel):
    target: str

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Target must not be empty")
        # strip scheme if given
        cleaned = re.sub(r"^https?://", "", v).split("/")[0].split(":")[0]
        if not (HOSTNAME_RE.match(cleaned) or IPV4_RE.match(cleaned)):
            raise ValueError("Target must be a valid hostname, URL, or IPv4 address")
        if len(v) > 255:
            raise ValueError("Target is too long")
        return v


class ServiceOut(BaseModel):
    id: str
    port: int
    protocol: str
    service_name: str
    exposure: Optional[str]
    reachable: str

    class Config:
        from_attributes = True


class FindingOut(BaseModel):
    id: str
    service_id: Optional[str] = None
    title: str
    risk: str
    reason: Optional[str]
    business_impact: Optional[str]
    detection_considerations: Optional[str]
    recommended_controls: Optional[List[str]]
    finding_type: str

    class Config:
        from_attributes = True


class ScanOut(BaseModel):
    id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    error_message: Optional[str]
    target: Optional[str] = None
    resolved_host: Optional[str] = None
    services: List[ServiceOut] = []
    findings: List[FindingOut] = []

    class Config:
        from_attributes = True


class SecurityEventIn(BaseModel):
    source: str
    user: Optional[str] = None
    asset: Optional[str] = None
    event_type: str
    severity: Optional[str] = "INFO"
    context: Optional[dict] = None
    timestamp: Optional[datetime] = None


class SecurityEventOut(BaseModel):
    id: str
    event_code: str
    timestamp: datetime
    source: str
    user: Optional[str]
    asset: Optional[str]
    event_type: str
    severity: str
    status: str

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    id: str
    incident_code: str
    severity: str
    affected_identity: Optional[str]
    affected_asset: Optional[str]
    first_observed: Optional[datetime]
    last_observed: Optional[datetime]
    status: str
    summary: Optional[str]
    event_count: int = 0

    class Config:
        from_attributes = True


class IncidentDetailOut(IncidentOut):
    events: List[SecurityEventOut] = []


class AttackTechniqueOut(BaseModel):
    id: str
    name: str
    mitre_ref: Optional[str]
    description: Optional[str]
    detection_indicators: Optional[List[str]]
    defensive_controls: Optional[List[str]]
    affected_assets: Optional[List[str]]

    class Config:
        from_attributes = True


class DefenseRecommendationOut(BaseModel):
    id: str
    category: str
    recommendation: str

    class Config:
        from_attributes = True


class ResponseActionIn(BaseModel):
    incident_id: str
    action_type: str
    description: Optional[str] = None


class ResponseActionOut(BaseModel):
    id: str
    incident_id: str
    action_type: str
    description: Optional[str]
    performed_at: datetime

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    id: str
    timestamp: datetime
    actor: str
    action: str
    details: Optional[Any]

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str
