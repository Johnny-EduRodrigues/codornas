from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db
from siraback.models.associations import artifact_categories
from siraback.models.tenant import Tenant


class Category(db.Model):
    __tablename__ = "sb_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    tenant_id: Mapped[int] = mapped_column(ForeignKey("sb_tenant.id"))
    tenant: Mapped[Tenant] = relationship(back_populates="categories")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    artifacts: Mapped[list["Artifact"]] = relationship(
        secondary=artifact_categories,
        back_populates="categories",
    )
