from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from siraback.extensions import db


class AuthenticationIdentity(db.Model):
    __tablename__ = "sb_authentication_identity"
    __table_args__ = (
        UniqueConstraint(
            "login_provider_id",
            "identificator_external",
            name="uq_auth_identity_provider_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sb_user.id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="authentication_identities")
    login_provider_id: Mapped[int] = mapped_column(
        ForeignKey("sb_login_provider.id", ondelete="CASCADE"),
    )
    login_provider: Mapped["LoginProvider"] = relationship(
        back_populates="authentication_identities",
    )
    identificator_login: Mapped[str] = mapped_column(String(320))
    identificator_external: Mapped[str] = mapped_column(String(255))

    def to_dict(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "login_provider_id": self.login_provider_id,
            "identificator_login": self.identificator_login,
            "identificator_external": self.identificator_external,
        }
