from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Index, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UAS7Score(Base):
    __tablename__ = "uas7_scores"
    __table_args__ = (
        UniqueConstraint("user_id", "score_date", name="uq_user_score_date"),
        Index("idx_user_date", "user_id", "score_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    wheal_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-3
    itch_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-3
    notes: Mapped[str | None] = mapped_column(Text)
