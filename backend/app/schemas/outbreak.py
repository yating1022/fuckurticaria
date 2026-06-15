from datetime import datetime

from pydantic import BaseModel


# --- OutbreakDetail ---

class OutbreakDetailCreate(BaseModel):
    body_part: str | None = None
    symptom_type: str | None = None
    severity: int | None = None
    photo_id: int | None = None


class OutbreakDetailOut(OutbreakDetailCreate):
    id: int
    outbreak_id: int

    model_config = {"from_attributes": True}


# --- Outbreak ---

class OutbreakCreate(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    severity: int | None = None
    location_text: str | None = None
    notes: str | None = None
    trigger_guess: str | None = None


class OutbreakUpdate(BaseModel):
    started_at: datetime | None = None
    ended_at: datetime | None = None
    severity: int | None = None
    location_text: str | None = None
    notes: str | None = None
    trigger_guess: str | None = None


class OutbreakOut(BaseModel):
    id: int
    user_id: int
    started_at: datetime
    ended_at: datetime | None
    severity: int | None
    location_text: str | None
    notes: str | None
    trigger_guess: str | None
    created_at: datetime
    details: list[OutbreakDetailOut] = []

    model_config = {"from_attributes": True}
