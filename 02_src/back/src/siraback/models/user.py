from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db
from siraback.models.associations import (
    artifact_admins,
    reservation_observers,
    reservation_takers,
    user_tenants,
)


class User(db.Model):
    __tablename__ = "sb_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    email: Mapped[str] = mapped_column(String(320))
    timestamp_email_verified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    password: Mapped[str] = mapped_column(String(255))
    obs: Mapped[str | None] = mapped_column(Text, nullable=True)
    super_admin: Mapped[bool] = mapped_column(Boolean)
    active: Mapped[bool] = mapped_column(Boolean)
    tenants: Mapped[list["Tenant"]] = relationship(
        secondary=user_tenants,
        back_populates="users",
    )
    artifacts_admin: Mapped[list["Artifact"]] = relationship(
        secondary=artifact_admins,
        back_populates="admins",
    )
    reservations_observer: Mapped[list["Reservation"]] = relationship(
        secondary=reservation_observers,
        back_populates="observers",
    )
    reservations_taker: Mapped[list["Reservation"]] = relationship(
        secondary=reservation_takers,
        back_populates="takers",
    )
