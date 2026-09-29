from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["assets"])


@router.get("/api/assets")
def list_assets(db: Session = Depends(get_db)):
    assets = db.query(models.Asset).all()
    return [
        {"id": a.id, "name": a.name, "asset_type": a.asset_type, "description": a.description}
        for a in assets
    ]


@router.get("/api/attack-techniques", response_model=list[schemas.AttackTechniqueOut])
def list_attack_techniques(db: Session = Depends(get_db)):
    return db.query(models.AttackTechnique).all()
