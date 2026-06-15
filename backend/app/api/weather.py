from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.weather import WeatherSnapshot
from app.schemas.weather import CityOut, CityUpdate, WeatherSnapshotOut
from app.services.weather import fetch_and_store

router = APIRouter(prefix="/api/weather", tags=["weather"])

DEFAULT_USER_ID = 1


@router.get("/current", response_model=WeatherSnapshotOut | None)
def get_current(db: Session = Depends(get_db)):
    snap = (
        db.query(WeatherSnapshot)
        .filter(WeatherSnapshot.user_id == DEFAULT_USER_ID)
        .order_by(WeatherSnapshot.snapshot_at.desc())
        .first()
    )
    return snap


@router.post("/refresh", response_model=WeatherSnapshotOut | None)
def refresh_weather():
    snap = fetch_and_store(DEFAULT_USER_ID)
    return snap


@router.get("/history", response_model=list[WeatherSnapshotOut])
def get_history(
    days: int = Query(7, ge=1, le=365),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(WeatherSnapshot).filter(WeatherSnapshot.user_id == DEFAULT_USER_ID)
    if start:
        q = q.filter(WeatherSnapshot.snapshot_at >= start)
    else:
        q = q.filter(WeatherSnapshot.snapshot_at >= datetime.now() - timedelta(days=days))
    if end:
        q = q.filter(WeatherSnapshot.snapshot_at <= end)
    return q.order_by(WeatherSnapshot.snapshot_at.asc()).limit(2000).all()


@router.get("/city", response_model=CityOut)
def get_city():
    return CityOut(city=settings.QWEATHER_CITY, location_id=settings.QWEATHER_LOCATION_ID)
