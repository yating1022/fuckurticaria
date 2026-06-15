from datetime import datetime, time

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MedicationReminder(Base):
    __tablename__ = "medication_reminders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    medication_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("medications.id"), nullable=False
    )
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    days_of_week: Mapped[str | None] = mapped_column(String(20))  # 1,2,3,4,5,6,7
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    dose: Mapped[str | None] = mapped_column(String(50))
    last_ack_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    medication: Mapped["Medication"] = relationship("Medication")


class WithdrawalObservation(Base):
    __tablename__ = "withdrawal_observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    medication_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("medications.id"), nullable=False
    )
    original_dose: Mapped[str | None] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active / completed / cancelled
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
