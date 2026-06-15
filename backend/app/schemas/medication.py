from datetime import datetime

from pydantic import BaseModel


# --- Medication ---

class MedicationCreate(BaseModel):
    name: str
    category: str | None = None
    default_dose: str | None = None


class MedicationUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    default_dose: str | None = None


class MedicationOut(BaseModel):
    id: int
    user_id: int | None
    name: str
    category: str | None
    default_dose: str | None
    is_system: bool

    model_config = {"from_attributes": True}


# --- MedicationRecord ---

class MedicationRecordCreate(BaseModel):
    medication_id: int
    dose: str
    taken_at: datetime
    notes: str | None = None
    is_prn: bool = False
    effectiveness: int | None = None
    side_effects: list[str] | None = None
    feedback_note: str | None = None


class MedicationRecordUpdate(BaseModel):
    effectiveness: int | None = None
    side_effects: list[str] | None = None
    feedback_note: str | None = None


class MedicationRecordOut(BaseModel):
    id: int
    user_id: int
    medication_id: int
    dose: str
    taken_at: datetime
    notes: str | None
    is_prn: bool
    effectiveness: int | None
    side_effects: list[str] | None
    feedback_note: str | None
    created_at: datetime
    medication: MedicationOut | None = None

    model_config = {"from_attributes": True}
