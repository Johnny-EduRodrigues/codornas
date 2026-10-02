from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Time,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_reservation_time_range"),
        CheckConstraint(
            "(active = 1 AND canceler_user_id IS NULL AND canceler_annotation IS NULL) "
            "OR (active = 0 AND canceler_user_id IS NOT NULL "
            "AND canceler_annotation IS NOT NULL)",
            name="ck_reservation_cancellation_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    artifact_id: Mapped[int] = mapped_column(ForeignKey("artifacts.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    purpose: Mapped[str] = mapped_column(String(250), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    batch_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    obs: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    canceler_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    canceler_annotation: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(
        back_populates="reservations", foreign_keys=[user_id]
    )
    artifact: Mapped["Artifact"] = relationship(back_populates="reservations")
    canceler_user: Mapped["User | None"] = relationship(
        back_populates="canceled_reservations", foreign_keys=[canceler_user_id]
    )
