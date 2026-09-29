from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["defenses"])


@router.get("/api/defenses", response_model=list[schemas.DefenseRecommendationOut])
def list_defenses(db: Session = Depends(get_db)):
    return db.query(models.DefenseRecommendation).all()


@router.get("/api/audit-logs", response_model=list[schemas.AuditLogOut])
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(200).all()
