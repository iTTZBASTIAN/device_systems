"""Baseline de usuarios compatible con instalaciones EV09.

Revision ID: ev10_users
Revises:
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa


revision = "ev10_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)

    existing_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_id" not in existing_indexes:
        op.create_index("ix_users_id", "users", ["id"], unique=False)
    if "ix_users_email" not in existing_indexes:
        op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("users"):
        op.drop_table("users")