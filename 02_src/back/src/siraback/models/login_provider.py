from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db


class LoginProvider(db.Model):
    __tablename__ = "sb_login_provider"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(250))
    authentication_identities: Mapped[list["AuthenticationIdentity"]] = relationship(
        back_populates="login_provider",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
