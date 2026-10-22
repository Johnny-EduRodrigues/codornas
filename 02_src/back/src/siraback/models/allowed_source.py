from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db


class AllowedSource(db.Model):
    __tablename__ = "sb_allowed_source"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(250))
    filter_or_email_allowed: Mapped[str] = mapped_column(String(320))
    type: Mapped[str] = mapped_column(String(20))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("sb_tenant.id"))
    tenant: Mapped["Tenant"] = relationship()
