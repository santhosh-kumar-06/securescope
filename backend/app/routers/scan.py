import time
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import scanner, risk_engine
from ..services.audit import log_action

router = APIRouter(tags=["scan"])


@router.post("/api/scan", response_model=schemas.ScanOut)
def start_scan(payload: schemas.ScanCreateRequest, demo: bool = False, db: Session = Depends(get_db)):
    target = models.Target(id=str(uuid.uuid4()), raw_input=payload.target)
    db.add(target)
    db.flush()

    scan = models.Scan(id=str(uuid.uuid4()), target_id=target.id, status=models.ScanStatus.SCANNING)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    started = time.monotonic()
    try:
        resolved_host, results = scanner.run_safe_scan(payload.target, demo_mode=demo)
        target.resolved_host = resolved_host

        for r in results:
            svc = models.Service(
                id=str(uuid.uuid4()),
                scan_id=scan.id,
                port=r.port,
                protocol="tcp",
                service_name=r.service_name,
                exposure=r.exposure,
                reachable=r.reachable,
            )
            db.add(svc)
            db.flush()

            if r.reachable == "open":
                finding_data = risk_engine.build_finding_for_service(r.service_name)
                finding = models.Finding(
                    id=str(uuid.uuid4()),
                    scan_id=scan.id,
                    service_id=svc.id,
                    **finding_data,
                )
                db.add(finding)

        scan.status = models.ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        scan.duration_ms = int((time.monotonic() - started) * 1000)
        db.commit()
        db.refresh(scan)

        log_action(db, "scan.completed", {"scan_id": scan.id, "target": payload.target, "demo": demo})

    except scanner.ScanError as exc:
        scan.status = models.ScanStatus.FAILED
        scan.error_message = str(exc)
        scan.completed_at = datetime.utcnow()
        db.commit()
        log_action(db, "scan.failed", {"scan_id": scan.id, "error": str(exc)})
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        scan.status = models.ScanStatus.FAILED
        scan.error_message = "Unexpected error during scan. See server logs."
        scan.completed_at = datetime.utcnow()
        db.commit()
        log_action(db, "scan.failed", {"scan_id": scan.id, "error": "internal"})
        raise HTTPException(status_code=500, detail="Scan failed unexpectedly. Please try again.")

    return _scan_to_out(scan, target)


@router.get("/api/scans/{scan_id}", response_model=schemas.ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    target = db.query(models.Target).filter(models.Target.id == scan.target_id).first()
    return _scan_to_out(scan, target)


@router.get("/api/services", response_model=list[schemas.ServiceOut])
def list_services(scan_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Service)
    if scan_id:
        q = q.filter(models.Service.scan_id == scan_id)
    return q.all()


@router.get("/api/findings", response_model=list[schemas.FindingOut])
def list_findings(scan_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Finding)
    if scan_id:
        q = q.filter(models.Finding.scan_id == scan_id)
    return q.all()


def _scan_to_out(scan: models.Scan, target: models.Target | None) -> schemas.ScanOut:
    return schemas.ScanOut(
        id=scan.id,
        status=scan.status.value if hasattr(scan.status, "value") else scan.status,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        duration_ms=scan.duration_ms,
        error_message=scan.error_message,
        target=target.raw_input if target else None,
        resolved_host=target.resolved_host if target else None,
        services=[schemas.ServiceOut.model_validate(s) for s in scan.services],
        findings=[
            schemas.FindingOut(
                id=f.id, service_id=f.service_id, title=f.title,
                risk=f.risk.value if hasattr(f.risk, "value") else f.risk,
                reason=f.reason, business_impact=f.business_impact,
                detection_considerations=f.detection_considerations,
                recommended_controls=f.recommended_controls,
                finding_type=f.finding_type,
            ) for f in scan.findings
        ],
    )
