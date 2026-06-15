from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.uas7 import UAS7Score
from app.schemas.uas7 import (
    TrendPoint,
    UAS7Create,
    UAS7Out,
    UAS7Trend,
    WeeklySummary,
)

router = APIRouter(prefix="/api/uas7", tags=["uas7"])

DEFAULT_USER_ID = 1

UAS7_LEVELS = [
    (0, "无症状", "#4ade80"),
    (6, "轻度", "#facc15"),
    (15, "中度", "#fb923c"),
    (27, "重度", "#f87171"),
    (42, "极重度", "#dc2626"),
]


def classify_uas7(score: int) -> tuple[str, str]:
    for max_val, label, color in UAS7_LEVELS:
        if score <= max_val:
            return label, color
    return "极重度", "#dc2626"


def get_week_range(d: date) -> tuple[date, date]:
    start = d - timedelta(days=d.weekday())
    return start, start + timedelta(days=6)


def _score_to_out(s: UAS7Score) -> UAS7Out:
    out = UAS7Out.model_validate(s)
    out.daily_score = s.wheal_score + s.itch_score
    return out


def _zero_out(d: date) -> UAS7Out:
    return UAS7Out(id=0, user_id=DEFAULT_USER_ID, score_date=d,
                   wheal_score=0, itch_score=0, notes=None, daily_score=0)


def _week_scores(db: Session, week_start: date) -> tuple[list[UAS7Out], int]:
    """Return full 7-day array (missing days = 0) and count of manually recorded days."""
    records = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == DEFAULT_USER_ID,
                UAS7Score.score_date >= week_start,
                UAS7Score.score_date <= week_start + timedelta(days=6))
        .all()
    )
    by_date = {r.score_date: _score_to_out(r) for r in records}
    daily = [by_date.get(week_start + timedelta(days=i), _zero_out(week_start + timedelta(days=i)))
             for i in range(7)]
    return daily, len(records)


@router.post("", response_model=UAS7Out)
def submit_score(body: UAS7Create, db: Session = Depends(get_db)):
    if not 0 <= body.wheal_score <= 3 or not 0 <= body.itch_score <= 3:
        from fastapi import HTTPException
        raise HTTPException(400, "评分必须在 0-3 之间")

    existing = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == DEFAULT_USER_ID, UAS7Score.score_date == body.score_date)
        .first()
    )
    if existing:
        existing.wheal_score = body.wheal_score
        existing.itch_score = body.itch_score
        existing.notes = body.notes
        db.commit()
        db.refresh(existing)
        return _score_to_out(existing)

    score = UAS7Score(user_id=DEFAULT_USER_ID, **body.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return _score_to_out(score)


@router.delete("")
def delete_score(date: date = Query(...), db: Session = Depends(get_db)):
    score = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == DEFAULT_USER_ID, UAS7Score.score_date == date)
        .first()
    )
    if not score:
        from fastapi import HTTPException
        raise HTTPException(404, "该日期无手动记录")
    db.delete(score)
    db.commit()
    return {"ok": True, "date": date.isoformat()}


@router.get("", response_model=UAS7Out)
def get_daily(date: date = Query(...), db: Session = Depends(get_db)):
    score = (
        db.query(UAS7Score)
        .filter(UAS7Score.user_id == DEFAULT_USER_ID, UAS7Score.score_date == date)
        .first()
    )
    return _score_to_out(score) if score else _zero_out(date)


@router.get("/weekly", response_model=WeeklySummary)
def get_weekly(date: date = Query(...), db: Session = Depends(get_db)):
    week_start, _ = get_week_range(date)
    daily, recorded = _week_scores(db, week_start)
    total = sum(d.daily_score for d in daily)
    level, color = classify_uas7(total)

    return WeeklySummary(
        start_date=week_start,
        end_date=week_start + timedelta(days=6),
        uas7_score=total,
        level=level,
        color=color,
        days_scored=recorded,
        daily_scores=daily,
    )


@router.get("/trend", response_model=UAS7Trend)
def get_trend(weeks: int = Query(12, ge=1, le=52), db: Session = Depends(get_db)):
    today = date.today()
    current_week_start, _ = get_week_range(today)
    data: list[TrendPoint] = []

    for i in range(weeks - 1, -1, -1):
        ws = current_week_start - timedelta(weeks=i)
        daily, _ = _week_scores(db, ws)
        score = sum(d.daily_score for d in daily)
        level, color = classify_uas7(score)
        data.append(TrendPoint(week_start=ws, week_end=ws + timedelta(days=6),
                               uas7_score=score, level=level, color=color))

    return UAS7Trend(weeks=weeks, data=data)
