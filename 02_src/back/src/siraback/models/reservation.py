from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Time,
    Uuid,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db
from siraback.models.associations import reservation_observers, reservation_takers


class Reservation(db.Model):
    __tablename__ = "sb_reservation"
    __table_args__ = (
        CheckConstraint(
            "active OR (canceled_by_user_id IS NOT NULL "
            "AND cancellation_reason IS NOT NULL)",
            name="ck_reservation_cancellation_details",
        ),
        CheckConstraint(
            "canceled_by_user_id IS NULL OR NOT active",
            name="ck_reservation_canceled_user_inactive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sb_user.id"))
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    artifact_id: Mapped[int] = mapped_column(ForeignKey("sb_artifact.id"))
    artifact: Mapped["Artifact"] = relationship()
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    purpose_id: Mapped[int] = mapped_column(ForeignKey("sb_purpose.id"))
    purpose: Mapped["Purpose"] = relationship()
    active: Mapped[bool] = mapped_column(default=True, server_default=true())
    batch_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    obs: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    canceled_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("sb_user.id"),
        nullable=True,
    )
    canceled_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[canceled_by_user_id],
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("sb_reservation.id"),
        unique=True,
        nullable=True,
    )
    previous_reservation: Mapped["Reservation | None"] = relationship(
        remote_side="Reservation.id",
        foreign_keys=[previous_reservation_id],
        uselist=False,
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("sb_group.id"),
        nullable=True,
    )
    group: Mapped["Group | None"] = relationship()
    takers: Mapped[list["User"]] = relationship(
        secondary=reservation_takers,
        back_populates="reservations_taker",
    )
    observers: Mapped[list["User"]] = relationship(
        secondary=reservation_observers,
        back_populates="reservations_observer",
    )
