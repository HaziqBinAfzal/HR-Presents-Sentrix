"""add authentication state

Revision ID: 20260805_02
Revises: 20260805_01
"""

from alembic import op
import sqlalchemy as sa

revision = "20260805_02"
down_revision = "20260805_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_auth_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_auth_states_user_id", "user_auth_states", ["user_id"], unique=True)


def downgrade():
    op.drop_index("ix_user_auth_states_user_id", table_name="user_auth_states")
    op.drop_table("user_auth_states")
