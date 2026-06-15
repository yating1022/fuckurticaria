from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))  # 抗组胺/激素/生物制剂
    default_dose: Mapped[str | None] = mapped_column(String(50))
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)


class MedicationRecord(Base):
    __tablename__ = "medication_records"
    __table_args__ = (Index("idx_user_taken", "user_id", "taken_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    medication_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("medications.id"), nullable=False
    )
    dose: Mapped[str] = mapped_column(String(50), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    is_prn: Mapped[bool] = mapped_column(Boolean, default=False)
    effectiveness: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5 药效评分
    side_effects: Mapped[list | None] = mapped_column(JSON)  # ["嗜睡","头痛"]
    feedback_note: Mapped[str | None] = mapped_column(Text)  # 自由文本反馈
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    medication: Mapped["Medication"] = relationship()
