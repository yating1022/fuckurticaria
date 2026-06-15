from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from app.core.database import Base


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"
    __table_args__ = (Index("idx_user_snapshot", "user_id", "snapshot_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature: Mapped[float | None] = mapped_column(DECIMAL(5, 1))
    humidity: Mapped[int | None] = mapped_column(SmallInteger)
    pressure: Mapped[int | None] = mapped_column(SmallInteger)
    pollen_index: Mapped[int | None] = mapped_column(SmallInteger)
    aqi: Mapped[int | None] = mapped_column(SmallInteger)
    aqi_category: Mapped[str | None] = mapped_column(String(20))
    aqi_primary: Mapped[str | None] = mapped_column(String(20))
    pm25: Mapped[float | None] = mapped_column(DECIMAL(7, 1))
    pm10: Mapped[float | None] = mapped_column(DECIMAL(7, 1))
    no2: Mapped[float | None] = mapped_column(DECIMAL(7, 1))
    so2: Mapped[float | None] = mapped_column(DECIMAL(7, 1))
    co: Mapped[float | None] = mapped_column(DECIMAL(7, 2))
    o3: Mapped[float | None] = mapped_column(DECIMAL(7, 1))
    weather_desc: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(50))
