from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.outbreak import Outbreak, OutbreakDetail
from app.schemas.outbreak import (
    OutbreakCreate,
    OutbreakDetailCreate,
    OutbreakDetailOut,
    OutbreakOut,
    OutbreakUpdate,
)

router = APIRouter(prefix="/api/outbreaks", tags=["outbreaks"])

# 临时硬编码 user_id，后续接入认证后替换
DEFAULT_USER_ID = 1


@router.post("", response_model=OutbreakOut)
def create_outbreak(body: OutbreakCreate, db: Session = Depends(get_db)):
    outbreak = Outbreak(user_id=DEFAULT_USER_ID, **body.model_dump())
    db.add(outbreak)
    db.commit()
    db.refresh(outbreak)
    return outbreak


@router.get("", response_model=list[OutbreakOut])
def list_outbreaks(
    start: datetime | None = Query(None, description="起始时间"),
    end: datetime | None = Query(None, description="结束时间"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Outbreak)
        .options(joinedload(Outbreak.details))
        .filter(Outbreak.user_id == DEFAULT_USER_ID)
    )
    if start:
        q = q.filter(Outbreak.started_at >= start)
    if end:
        q = q.filter(Outbreak.started_at <= end)
    return q.order_by(Outbreak.started_at.desc()).offset((page - 1) * size).limit(size).all()


@router.get("/{outbreak_id}", response_model=OutbreakOut)
def get_outbreak(outbreak_id: int, db: Session = Depends(get_db)):
    outbreak = (
        db.query(Outbreak)
        .options(joinedload(Outbreak.details))
        .filter(Outbreak.id == outbreak_id, Outbreak.user_id == DEFAULT_USER_ID)
        .first()
    )
    if not outbreak:
        raise HTTPException(status_code=404, detail="发病记录不存在")
    return outbreak


@router.put("/{outbreak_id}", response_model=OutbreakOut)
def update_outbreak(outbreak_id: int, body: OutbreakUpdate, db: Session = Depends(get_db)):
    outbreak = (
        db.query(Outbreak)
        .filter(Outbreak.id == outbreak_id, Outbreak.user_id == DEFAULT_USER_ID)
        .first()
    )
    if not outbreak:
        raise HTTPException(status_code=404, detail="发病记录不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(outbreak, field, value)
    db.commit()
    db.refresh(outbreak)
    return outbreak


@router.delete("/{outbreak_id}")
def delete_outbreak(outbreak_id: int, db: Session = Depends(get_db)):
    outbreak = (
        db.query(Outbreak)
        .filter(Outbreak.id == outbreak_id, Outbreak.user_id == DEFAULT_USER_ID)
        .first()
    )
    if not outbreak:
        raise HTTPException(status_code=404, detail="发病记录不存在")
    db.delete(outbreak)
    db.commit()
    return {"detail": "已删除"}


# --- OutbreakDetail ---

@router.post("/{outbreak_id}/details", response_model=OutbreakDetailOut)
def add_detail(outbreak_id: int, body: OutbreakDetailCreate, db: Session = Depends(get_db)):
    outbreak = (
        db.query(Outbreak)
        .filter(Outbreak.id == outbreak_id, Outbreak.user_id == DEFAULT_USER_ID)
        .first()
    )
    if not outbreak:
        raise HTTPException(status_code=404, detail="发病记录不存在")
    detail = OutbreakDetail(outbreak_id=outbreak_id, **body.model_dump())
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail


@router.delete("/details/{detail_id}")
def delete_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = db.query(OutbreakDetail).filter(OutbreakDetail.id == detail_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="症状详情不存在")
    db.delete(detail)
    db.commit()
    return {"detail": "已删除"}
