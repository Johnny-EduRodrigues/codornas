"""Add a server default to the user creation timestamp.

Revision ID: 3b7c1a9e4d52
Revises: 9fdb2dc2b1ea
"""
from alembic import op
import sqlalchemy as sa


revision = "3b7c1a9e4d52"
down_revision = "9fdb2dc2b1ea"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )


def downgrade():
    with op.batch_alter_table("sb_user") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=None,
        )
