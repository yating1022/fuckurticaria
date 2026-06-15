from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.medication import Medication, MedicationRecord
from app.schemas.medication import (
    MedicationCreate,
    MedicationOut,
    MedicationRecordCreate,
    MedicationRecordOut,
    MedicationRecordUpdate,
    MedicationUpdate,
)

router = APIRouter(tags=["medications"])

DEFAULT_USER_ID = 1

SEED_MEDICATIONS = [
    {"name": "氯雷他定", "category": "二代抗组胺", "default_dose": "10mg"},
    {"name": "西替利嗪", "category": "二代抗组胺", "default_dose": "10mg"},
    {"name": "非索非那定", "category": "二代抗组胺", "default_dose": "180mg"},
    {"name": "苯海拉明", "category": "一代抗组胺", "default_dose": "25mg"},
    {"name": "氯苯那敏", "category": "一代抗组胺", "default_dose": "4mg"},
    {"name": "泼尼松", "category": "激素", "default_dose": "5mg"},
    {"name": "地塞米松", "category": "激素", "default_dose": "0.75mg"},
    {"name": "奥马珠单抗", "category": "生物制剂", "default_dose": "150mg"},
    {"name": "孟鲁司特", "category": "其他", "default_dose": "10mg"},
]


def seed_medications(db: Session):
    existing = db.query(Medication).filter(Medication.is_system == True).count()
    if existing == 0:
        for m in SEED_MEDICATIONS:
            db.add(Medication(is_system=True, user_id=None, **m))
        db.commit()


# --- Medications CRUD ---

@router.post("/api/medications", response_model=MedicationOut)
def create_medication(body: MedicationCreate, db: Session = Depends(get_db)):
    med = Medication(user_id=DEFAULT_USER_ID, is_system=False, **body.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/api/medications", response_model=list[MedicationOut])
def list_medications(db: Session = Depends(get_db)):
    seed_medications(db)
    return (
        db.query(Medication)
        .filter((Medication.user_id == DEFAULT_USER_ID) | (Medication.is_system == True))
        .order_by(Medication.category, Medication.name)
        .all()
    )


@router.put("/api/medications/{med_id}", response_model=MedicationOut)
def update_medication(med_id: int, body: MedicationUpdate, db: Session = Depends(get_db)):
    med = db.query(Medication).filter(Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="药物不存在")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(med, field, val)
    db.commit()
    db.refresh(med)
    return med


@router.delete("/api/medications/{med_id}")
def delete_medication(med_id: int, db: Session = Depends(get_db)):
    med = db.query(Medication).filter(Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="药物不存在")
    db.delete(med)
    db.commit()
    return {"detail": "已删除"}


# --- MedicationRecords CRUD ---

@router.post("/api/medication-records", response_model=MedicationRecordOut)
def create_record(body: MedicationRecordCreate, db: Session = Depends(get_db)):
    record = MedicationRecord(user_id=DEFAULT_USER_ID, **body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    record.medication = db.query(Medication).get(record.medication_id)
    return record


@router.get("/api/medication-records", response_model=list[MedicationRecordOut])
def list_records(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(MedicationRecord)
        .options(joinedload(MedicationRecord.medication))  # type: ignore[arg-type]
        .filter(MedicationRecord.user_id == DEFAULT_USER_ID)
    )
    if start:
        q = q.filter(MedicationRecord.taken_at >= start)
    if end:
        q = q.filter(MedicationRecord.taken_at <= end)
    return q.order_by(MedicationRecord.taken_at.desc()).limit(200).all()


@router.get("/api/medication-records/{rec_id}", response_model=MedicationRecordOut)
def get_record(rec_id: int, db: Session = Depends(get_db)):
    rec = (
        db.query(MedicationRecord)
        .options(joinedload(MedicationRecord.medication))  # type: ignore[arg-type]
        .filter(MedicationRecord.id == rec_id, MedicationRecord.user_id == DEFAULT_USER_ID)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="用药记录不存在")
    return rec


@router.put("/api/medication-records/{rec_id}", response_model=MedicationRecordOut)
def update_record(rec_id: int, body: MedicationRecordUpdate, db: Session = Depends(get_db)):
    rec = db.query(MedicationRecord).filter(
        MedicationRecord.id == rec_id, MedicationRecord.user_id == DEFAULT_USER_ID
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="用药记录不存在")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(rec, field, val)
    db.commit()
    db.refresh(rec)
    rec.medication = db.query(Medication).get(rec.medication_id)
    return rec


@router.delete("/api/medication-records/{rec_id}")
def delete_record(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(MedicationRecord).filter(
        MedicationRecord.id == rec_id, MedicationRecord.user_id == DEFAULT_USER_ID
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="用药记录不存在")
    db.delete(rec)
    db.commit()
    return {"detail": "已删除"}
