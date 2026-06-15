from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Outbreak(Base):
    __tablename__ = "outbreaks"
    __table_args__ = (Index("idx_user_started", "user_id", "started_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    severity: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    location_text: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    trigger_guess: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    details: Mapped[list["OutbreakDetail"]] = relationship(back_populates="outbreak")


class OutbreakDetail(Base):
    __tablename__ = "outbreak_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    outbreak_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("outbreaks.id"), nullable=False
    )
    body_part: Mapped[str | None] = mapped_column(String(50))
    symptom_type: Mapped[str | None] = mapped_column(String(50))  # 风团/瘙痒/肿胀
    severity: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    photo_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("photos.id"))

    outbreak: Mapped["Outbreak"] = relationship(back_populates="details")
