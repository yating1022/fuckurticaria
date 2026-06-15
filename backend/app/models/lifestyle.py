from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL, JSON

from app.core.database import Base


class LifestyleLog(Base):
    __tablename__ = "lifestyle_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="uq_user_log_date"),
        Index("idx_user_date", "user_id", "log_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_hours: Mapped[float | None] = mapped_column(DECIMAL(3, 1))
    sleep_quality: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    stress_level: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    exercise: Mapped[bool | None] = mapped_column(Boolean)
    diet_tags: Mapped[dict | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
