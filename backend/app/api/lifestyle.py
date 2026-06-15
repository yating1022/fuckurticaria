from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lifestyle import LifestyleLog
from app.schemas.lifestyle import CalendarDay, LifestyleCreate, LifestyleOut

router = APIRouter(prefix="/api/lifestyle", tags=["lifestyle"])

DEFAULT_USER_ID = 1


def _to_out(log: LifestyleLog) -> LifestyleOut:
    tags = log.diet_tags
    if isinstance(tags, list):
        pass
    elif tags is None:
        tags = None
    else:
        tags = list(tags) if tags else None
    return LifestyleOut(
        id=log.id,
        user_id=log.user_id,
        log_date=log.log_date,
        sleep_hours=float(log.sleep_hours) if log.sleep_hours is not None else None,
        sleep_quality=log.sleep_quality,
        stress_level=log.stress_level,
        exercise=log.exercise,
        diet_tags=tags,
        notes=log.notes,
        created_at=log.created_at,
    )


@router.post("", response_model=LifestyleOut)
def submit_log(body: LifestyleCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(LifestyleLog)
        .filter(LifestyleLog.user_id == DEFAULT_USER_ID, LifestyleLog.log_date == body.log_date)
        .first()
    )
    if existing:
        for field, val in body.model_dump(exclude={"log_date"}).items():
            setattr(existing, field, val)
        db.commit()
        db.refresh(existing)
        return _to_out(existing)

    log = LifestyleLog(
        user_id=DEFAULT_USER_ID,
        log_date=body.log_date,
        sleep_hours=body.sleep_hours,
        sleep_quality=body.sleep_quality,
        stress_level=body.stress_level,
        exercise=body.exercise,
        diet_tags=body.diet_tags,
        notes=body.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _to_out(log)


@router.get("", response_model=LifestyleOut | list[LifestyleOut])
def get_logs(
    date: date | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(LifestyleLog).filter(LifestyleLog.user_id == DEFAULT_USER_ID)

    if date:
        log = q.filter(LifestyleLog.log_date == date).first()
        return _to_out(log) if log else None

    if start:
        q = q.filter(LifestyleLog.log_date >= start)
    if end:
        q = q.filter(LifestyleLog.log_date <= end)

    return [_to_out(l) for l in q.order_by(LifestyleLog.log_date.desc()).limit(100).all()]


@router.get("/calendar", response_model=list[CalendarDay])
def calendar(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    rows = (
        db.query(LifestyleLog.log_date)
        .filter(
            LifestyleLog.user_id == DEFAULT_USER_ID,
            LifestyleLog.log_date >= first_day,
            LifestyleLog.log_date <= last_day,
        )
        .all()
    )
    recorded = {r[0] for r in rows}

    days = []
    d = first_day
    while d <= last_day:
        days.append(CalendarDay(log_date=d, has_record=d in recorded))
        d += timedelta(days=1)
    return days
