from datetime import date, datetime

from pydantic import BaseModel


class LifestyleCreate(BaseModel):
    log_date: date
    sleep_hours: float | None = None
    sleep_quality: int | None = None
    stress_level: int | None = None
    exercise: bool | None = None
    diet_tags: list[str] | None = None
    notes: str | None = None


class LifestyleOut(BaseModel):
    id: int
    user_id: int
    log_date: date
    sleep_hours: float | None
    sleep_quality: int | None
    stress_level: int | None
    exercise: bool | None
    diet_tags: list[str] | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CalendarDay(BaseModel):
    log_date: date
    has_record: bool
