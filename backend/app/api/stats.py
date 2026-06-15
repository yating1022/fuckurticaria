from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.outbreak import Outbreak
from app.schemas.stats import (
    FrequencyPoint,
    FrequencyResponse,
    HeatmapCell,
    HeatmapResponse,
    SeverityDistributionResponse,
    SeveritySlice,
)

router = APIRouter(prefix="/api/stats", tags=["stats"])

DEFAULT_USER_ID = 1

SEVERITY_LABELS = {1: "轻微", 2: "较轻", 3: "中度", 4: "较重", 5: "严重"}


@router.get("/outbreak-frequency", response_model=FrequencyResponse)
def outbreak_frequency(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
):
    if not end:
        end = datetime.now()
    if not start:
        start = end - timedelta(days=90)

    rows = (
        db.query(
            func.date(Outbreak.started_at).label("d"),
            func.count(Outbreak.id).label("cnt"),
            func.avg(Outbreak.severity).label("avg_sev"),
        )
        .filter(
            Outbreak.user_id == DEFAULT_USER_ID,
            Outbreak.started_at >= start,
            Outbreak.started_at <= end,
        )
        .group_by("d")
        .order_by("d")
        .all()
    )

    data = [
        FrequencyPoint(
            date=str(r.d),
            count=r.cnt,
            avg_severity=round(float(r.avg_sev), 1) if r.avg_sev else None,
        )
        for r in rows
    ]

    if granularity == "week":
        data = _aggregate(data, "%Y-W%W")
    elif granularity == "month":
        data = _aggregate(data, "%Y-%m")

    return FrequencyResponse(granularity=granularity, data=data)


def _aggregate(points: list[FrequencyPoint], fmt: str) -> list[FrequencyPoint]:
    from datetime import datetime as dt

    buckets: dict[str, list[FrequencyPoint]] = {}
    for p in points:
        key = dt.strptime(p.date, "%Y-%m-%d").strftime(fmt)
        buckets.setdefault(key, []).append(p)

    result = []
    for key, group in sorted(buckets.items()):
        total = sum(p.count for p in group)
        sevs = [p.avg_severity for p in group if p.avg_severity is not None]
        avg = round(sum(sevs) / len(sevs), 1) if sevs else None
        result.append(FrequencyPoint(date=key, count=total, avg_severity=avg))
    return result


@router.get("/outbreak-heatmap", response_model=HeatmapResponse)
def outbreak_heatmap(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.dayofweek(Outbreak.started_at).label("dow"),
            func.hour(Outbreak.started_at).label("h"),
            func.count(Outbreak.id).label("cnt"),
        )
        .filter(Outbreak.user_id == DEFAULT_USER_ID)
        .group_by("dow", "h")
        .all()
    )

    # MySQL DAYOF WEEK: 1=Sunday ... 7=Saturday → convert to 0=Mon..6=Sun
    data = []
    for r in rows:
        day = (int(r.dow) + 5) % 7  # 1→6(Sun), 2→0(Mon), ..., 7→5(Sat)
        data.append(HeatmapCell(day=day, hour=int(r.h), value=r.cnt))

    return HeatmapResponse(data=data)


@router.get("/severity-distribution", response_model=SeverityDistributionResponse)
def severity_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Outbreak.severity,
            func.count(Outbreak.id).label("cnt"),
        )
        .filter(Outbreak.user_id == DEFAULT_USER_ID, Outbreak.severity.isnot(None))
        .group_by(Outbreak.severity)
        .all()
    )

    total = sum(r.cnt for r in rows)
    data = [
        SeveritySlice(
            severity=r.severity,
            label=SEVERITY_LABELS.get(r.severity, f"等级{r.severity}"),
            count=r.cnt,
        )
        for r in sorted(rows, key=lambda x: x.severity)
    ]

    return SeverityDistributionResponse(total=total, data=data)
