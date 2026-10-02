from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    obs: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="user", foreign_keys="Reservation.user_id"
    )
    canceled_reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="canceler_user", foreign_keys="Reservation.canceler_user_id"
    )
