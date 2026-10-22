from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db


class Group(db.Model):
    __tablename__ = "sb_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    acronym: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(250))
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    obs: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    color: Mapped[str | None] = mapped_column(String(250), nullable=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("sb_tenant.id"))
    tenant: Mapped["Tenant"] = relationship()
