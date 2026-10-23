"""Seed the default Google provider and administrator account.

Revision ID: 8c2f6a1d4e73
Revises: 71a6b3c2d904
"""
import bcrypt
from alembic import op
import sqlalchemy as sa


revision = "8c2f6a1d4e73"
down_revision = "71a6b3c2d904"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    login_providers = sa.table(
        "sb_login_provider",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String(length=50)),
        sa.column("description", sa.String(length=250)),
    )
    google_provider = bind.execute(
        sa.select(login_providers.c.id).where(
            login_providers.c.name == "google",
        )
    ).first()
    if google_provider is None:
        bind.execute(
            login_providers.insert().values(
                name="google",
                description="Google",
            )
        )

    users = sa.table(
        "sb_user",
        sa.column("name", sa.String(length=250)),
        sa.column("email", sa.String(length=320)),
        sa.column("password", sa.String(length=255)),
        sa.column("super_admin", sa.Boolean()),
        sa.column("active", sa.Boolean()),
    )
    admin_exists = bind.execute(
        sa.select(users.c.email).where(
            users.c.email == "admin@admin.com",
        )
    ).first()
    if admin_exists is None:
        hashed_password = bcrypt.hashpw(
            b"admin",
            bcrypt.gensalt(),
        ).decode("utf-8")
        bind.execute(
            users.insert().values(
                name="admin",
                email="admin@admin.com",
                password=hashed_password,
                super_admin=True,
                active=True,
            )
        )


def downgrade():
    """Keep bootstrap data on downgrade because accounts may already use it."""
