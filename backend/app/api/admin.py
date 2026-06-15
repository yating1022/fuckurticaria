from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.setting import SystemSetting

router = APIRouter(prefix="/api/admin", tags=["admin"])


class SettingOut(BaseModel):
    key: str
    value: str | None
    description: str | None
    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: str
    description: str | None = None


SEED_SETTINGS = [
    ("deepseek_api_key", "", "DeepSeek API Key"),
    ("deepseek_base_url", "https://api.deepseek.com", "DeepSeek API Base URL"),
    ("deepseek_model", "deepseek-chat", "DeepSeek Model Name"),
]


def seed_settings(db: Session):
    for key, default, desc in SEED_SETTINGS:
        if not db.query(SystemSetting).filter(SystemSetting.key == key).first():
            db.add(SystemSetting(key=key, value=default, description=desc))
    db.commit()


@router.get("/settings", response_model=list[SettingOut])
def list_settings(db: Session = Depends(get_db)):
    seed_settings(db)
    return db.query(SystemSetting).order_by(SystemSetting.key).all()


@router.get("/settings/{key}", response_model=SettingOut)
def get_setting(key: str, db: Session = Depends(get_db)):
    seed_settings(db)
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not s:
        raise HTTPException(404, "设置项不存在")
    return s


@router.put("/settings/{key}", response_model=SettingOut)
def update_setting(key: str, body: SettingUpdate, db: Session = Depends(get_db)):
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not s:
        s = SystemSetting(key=key, value=body.value, description=body.description)
        db.add(s)
    else:
        s.value = body.value
        if body.description is not None:
            s.description = body.description
    db.commit()
    db.refresh(s)
    return s
