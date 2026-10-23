from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, false, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db
from siraback.models.associations import artifact_admins, artifact_categories


class Artifact(db.Model):
    __tablename__ = "sb_artifact"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    categories: Mapped[list["Category"]] = relationship(
        secondary=artifact_categories,
        back_populates="artifacts",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    tenant_id: Mapped[int] = mapped_column(ForeignKey("sb_tenant.id"))
    tenant: Mapped["Tenant"] = relationship()
    restrict: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    admins: Mapped[list["User"]] = relationship(
        secondary=artifact_admins,
        back_populates="artifacts_admin",
    )

    def to_dict(self) -> dict[str, int | str | bool]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "tenant_id": self.tenant_id,
            "restrict": self.restrict,
            "active": self.active,
        }
