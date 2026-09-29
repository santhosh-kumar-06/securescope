import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Severity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScanStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IncidentStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    MONITORING = "MONITORING"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"


class Target(Base):
    __tablename__ = "targets"
    id = Column(String, primary_key=True, default=gen_uuid)
    raw_input = Column(String, nullable=False)
    resolved_host = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="target")


class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, default=gen_uuid)
    target_id = Column(String, ForeignKey("targets.id"))
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)

    target = relationship("Target", back_populates="scans")
    services = relationship("Service", back_populates="scan")
    findings = relationship("Finding", back_populates="scan")


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    asset_type = Column(String)  # e.g. "web-app", "identity-system", "clinical-scheduling"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Service(Base):
    __tablename__ = "services"
    id = Column(String, primary_key=True, default=gen_uuid)
    scan_id = Column(String, ForeignKey("scans.id"))
    port = Column(Integer, nullable=False)
    protocol = Column(String, default="tcp")
    service_name = Column(String, nullable=False)
    exposure = Column(String)
    reachable = Column(String, default="unknown")  # open / closed / filtered / unknown

    scan = relationship("Scan", back_populates="services")


class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, default=gen_uuid)
    scan_id = Column(String, ForeignKey("scans.id"))
    service_id = Column(String, ForeignKey("services.id"), nullable=True)
    title = Column(String, nullable=False)
    risk = Column(Enum(Severity), default=Severity.INFO)
    reason = Column(Text)
    business_impact = Column(Text)
    detection_considerations = Column(Text)
    recommended_controls = Column(JSON)  # list[str]
    finding_type = Column(String, default="SECURITY_EXPOSURE")  # OPEN_SERVICE / CONFIRMED_VULNERABILITY / SECURITY_EXPOSURE

    scan = relationship("Scan", back_populates="findings")


class AttackTechnique(Base):
    __tablename__ = "attack_techniques"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    mitre_ref = Column(String, nullable=True)
    description = Column(Text)
    detection_indicators = Column(JSON)  # list[str]
    defensive_controls = Column(JSON)  # list[str]
    affected_assets = Column(JSON)  # list[str]


class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(String, primary_key=True, default=gen_uuid)
    event_code = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    user = Column(String, nullable=True)
    asset = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    severity = Column(Enum(Severity), default=Severity.INFO)
    status = Column(String, default="New")
    raw_context = Column(JSON, nullable=True)  # for detection engine evaluation

    incident_events = relationship("IncidentEvent", back_populates="event")


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True, default=gen_uuid)
    incident_code = Column(String, unique=True, nullable=False)
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    affected_identity = Column(String, nullable=True)
    affected_asset = Column(String, nullable=True)
    first_observed = Column(DateTime, nullable=True)
    last_observed = Column(DateTime, nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.MONITORING)
    summary = Column(Text, nullable=True)

    incident_events = relationship("IncidentEvent", back_populates="incident")


class IncidentEvent(Base):
    __tablename__ = "incident_events"
    id = Column(String, primary_key=True, default=gen_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"))
    event_id = Column(String, ForeignKey("security_events.id"))
    rule_id = Column(String, nullable=True)
    rule_reason = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="incident_events")
    event = relationship("SecurityEvent", back_populates="incident_events")


class DefenseRecommendation(Base):
    __tablename__ = "defense_recommendations"
    id = Column(String, primary_key=True, default=gen_uuid)
    category = Column(String, nullable=False)  # Asset & Exposure Mgmt, IAM, etc.
    recommendation = Column(Text, nullable=False)
    related_incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)


class ResponseAction(Base):
    __tablename__ = "response_actions"
    id = Column(String, primary_key=True, default=gen_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"))
    action_type = Column(String, nullable=False)
    description = Column(Text)
    simulated = Column(String, default="true")
    performed_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=gen_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor = Column(String, default="system")
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
