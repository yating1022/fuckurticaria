from datetime import date

from pydantic import BaseModel


class UAS7Create(BaseModel):
    score_date: date
    wheal_score: int
    itch_score: int
    notes: str | None = None


class UAS7Out(BaseModel):
    id: int
    user_id: int
    score_date: date
    wheal_score: int
    itch_score: int
    notes: str | None
    daily_score: int | None = None

    model_config = {"from_attributes": True}


class WeeklySummary(BaseModel):
    start_date: date
    end_date: date
    uas7_score: int
    level: str
    color: str
    days_scored: int
    daily_scores: list[UAS7Out]


class TrendPoint(BaseModel):
    week_start: date
    week_end: date
    uas7_score: int
    level: str
    color: str


class UAS7Trend(BaseModel):
    weeks: int
    data: list[TrendPoint]
