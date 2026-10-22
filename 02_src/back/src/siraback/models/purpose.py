from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db


class Purpose(db.Model):
    __tablename__ = "sb_purpose"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    tenant_id: Mapped[int] = mapped_column(ForeignKey("sb_tenant.id"))
    tenant: Mapped["Tenant"] = relationship()
