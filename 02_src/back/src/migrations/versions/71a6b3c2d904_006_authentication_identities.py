"""Add login providers and external authentication identities.

Revision ID: 71a6b3c2d904
Revises: 5e0c9d7a2b41
"""
from alembic import op
import sqlalchemy as sa


revision = "71a6b3c2d904"
down_revision = "5e0c9d7a2b41"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sb_login_provider",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=250), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(
        sa.table(
            "sb_login_provider",
            sa.column("name", sa.String()),
            sa.column("description", sa.String()),
        ),
        [{"name": "google", "description": "Google"}],
    )
    op.create_table(
        "sb_authentication_identity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("login_provider_id", sa.Integer(), nullable=False),
        sa.Column("identificator_login", sa.String(length=320), nullable=False),
        sa.Column("identificator_external", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["login_provider_id"],
            ["sb_login_provider.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["sb_user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "login_provider_id",
            "identificator_external",
            name="uq_auth_identity_provider_external",
        ),
    )
    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            existing_nullable=False,
            nullable=True,
        )
        batch_op.drop_column("auth_provider")


def downgrade():
    bind = op.get_bind()
    null_password_users = bind.execute(
        sa.text("SELECT COUNT(*) FROM sb_user WHERE password IS NULL")
    ).scalar_one()
    if null_password_users:
        raise RuntimeError(
            "Cannot downgrade while users have no local password; "
            "restore local passwords before downgrading."
        )

    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.add_column(
            sa.Column(
                "auth_provider",
                sa.String(length=50),
                server_default="local",
                nullable=False,
            )
        )
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            existing_nullable=True,
            nullable=False,
        )
    op.drop_table("sb_authentication_identity")
    op.drop_table("sb_login_provider")
