"""
Seeds the fictional Problem 4 demo dataset so the dashboard is fully
usable without a live/reachable target.

Run with:  python -m app.seed
"""
import uuid
from datetime import datetime, timedelta

from .database import Base, engine, SessionLocal
from . import models
from .services import risk_engine
from .services.knowledge_base import ATTACK_TECHNIQUES, DEFENSE_RECOMMENDATIONS

DEMO_TARGET_HOST = "healthcare.example.org"
DEMO_RESOLVED_IP = "203.0.113.10"  # RFC 5737 documentation range — not a real host

# Base day for the scenario timeline
BASE_DAY = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


def _t(hour: int, minute: int) -> datetime:
    return BASE_DAY + timedelta(hours=hour, minutes=minute)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Target).count() > 0:
            print("Demo data already present — skipping seed.")
            return

        # --- Target / Scan / Services / Findings ---
        target = models.Target(
            id=str(uuid.uuid4()),
            raw_input=DEMO_TARGET_HOST,
            resolved_host=DEMO_RESOLVED_IP,
        )
        db.add(target)
        db.flush()

        scan = models.Scan(
            id=str(uuid.uuid4()),
            target_id=target.id,
            status=models.ScanStatus.COMPLETED,
            started_at=_t(8, 10),
            completed_at=_t(8, 11),
            duration_ms=45000,
        )
        db.add(scan)
        db.flush()

        demo_services = [
            (22, "SSH", "Administrative service"),
            (53, "DNS", "Internal resolver"),
            (443, "HTTPS", "Public application endpoint"),
            (3389, "RDP", "Management service"),
        ]
        for port, name, exposure in demo_services:
            svc = models.Service(
                id=str(uuid.uuid4()),
                scan_id=scan.id,
                port=port,
                protocol="tcp",
                service_name=name,
                exposure=exposure,
                reachable="open",
            )
            db.add(svc)
            db.flush()
            finding_data = risk_engine.build_finding_for_service(name)
            db.add(models.Finding(
                id=str(uuid.uuid4()),
                scan_id=scan.id,
                service_id=svc.id,
                **finding_data,
            ))

        # --- Assets ---
        for name, atype, desc in [
            ("Patient Records System", "clinical-data", "EHR platform holding patient history."),
            ("Clinical Scheduling", "clinical-ops", "Appointment and care-coordination scheduling."),
            ("Administrative Systems", "corporate-it", "Billing, HR, and operational systems."),
            ("Identity Provider", "identity", "Central authentication and recovery-code issuance."),
        ]:
            db.add(models.Asset(id=str(uuid.uuid4()), name=name, asset_type=atype, description=desc))

        # --- Attack techniques ---
        for tech in ATTACK_TECHNIQUES:
            db.add(models.AttackTechnique(id=str(uuid.uuid4()), **tech))

        # --- Defense recommendations ---
        for category, rec in DEFENSE_RECOMMENDATIONS:
            db.add(models.DefenseRecommendation(id=str(uuid.uuid4()), category=category, recommendation=rec))

        db.commit()

        # --- Security events matching the Problem 4 timeline ---
        demo_events = [
            (_t(8, 10), "203.0.113.10", None, None, "External service discovery", "MEDIUM"),
            (_t(8, 24), "198.51.100.22", "admin01", "Identity Provider", "recovery-code usage", "HIGH"),
            (_t(9, 5), "198.51.100.22", "admin01", "Patient Records System", "sensitive resource access", "HIGH"),
            (_t(10, 40), "198.51.100.22", "admin01", "Clinical Scheduling", "potential lateral movement indicator", "HIGH"),
            (_t(13, 15), "198.51.100.45", "admin01", "Patient Records System", "suspicious outbound transfer", "CRITICAL"),
            (_t(15, 0), "system", "secops", "Identity Provider", "configuration change", "INFO"),
        ]
        count = 0
        for ts, source, user, asset, event_type, severity in demo_events:
            count += 1
            db.add(models.SecurityEvent(
                id=str(uuid.uuid4()),
                event_code=f"SEC-{count:05d}",
                timestamp=ts,
                source=source,
                user=user,
                asset=asset,
                event_type=event_type,
                severity=severity,
                status="Investigating" if severity in ("HIGH", "CRITICAL") else "Closed",
                raw_context={"scenario": "Problem 4 demo"},
            ))
        db.commit()

        db.add(models.AuditLog(id=str(uuid.uuid4()), actor="system", action="demo.seeded",
                                details={"target": DEMO_TARGET_HOST}))
        db.commit()

        print("Demo dataset seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
