"""Add authentication provider to users.

Revision ID: 5e0c9d7a2b41
Revises: 3b7c1a9e4d52
"""
from alembic import op
import sqlalchemy as sa


revision = "5e0c9d7a2b41"
down_revision = "3b7c1a9e4d52"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.add_column(
            sa.Column(
                "auth_provider",
                sa.String(length=50),
                server_default="local",
                nullable=False,
            )
        )


def downgrade():
    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.drop_column("auth_provider")
