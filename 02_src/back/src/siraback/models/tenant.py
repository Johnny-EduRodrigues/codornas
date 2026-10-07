from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from siraback.config import db

class Tenant(db.Model):
    __tablename__ = "sb_tenant"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))