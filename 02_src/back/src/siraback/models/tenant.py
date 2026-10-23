from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db
from siraback.models.associations import user_tenants


class Tenant(db.Model):
    __tablename__ = "sb_tenant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    categories: Mapped[list["Category"]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(
        secondary=user_tenants,
        back_populates="tenants",
    )

    # objeto em formato de dicionário,
    # para ser usado na camada de API
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }