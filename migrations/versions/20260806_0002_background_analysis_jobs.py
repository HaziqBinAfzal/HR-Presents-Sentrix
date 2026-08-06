"""Add background analysis jobs.

Revision ID: 20260806_0002
Revises: 20260806_0001
"""

from alembic import op
import sqlalchemy as sa


revision = "20260806_0002"
down_revision = "20260806_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="queued", nullable=False),
        sa.Column("progress", sa.Integer(), server_default="0", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"]),
    )
    op.create_index("ix_analysis_jobs_project_id", "analysis_jobs", ["project_id"])
    op.create_index("ix_analysis_jobs_user_id", "analysis_jobs", ["user_id"])
    op.create_index("ix_analysis_jobs_analysis_id", "analysis_jobs", ["analysis_id"])
    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])
    op.create_index("ix_analysis_jobs_created_at", "analysis_jobs", ["created_at"])


def downgrade():
    op.drop_index("ix_analysis_jobs_created_at", table_name="analysis_jobs")
    op.drop_index("ix_analysis_jobs_status", table_name="analysis_jobs")
    op.drop_index("ix_analysis_jobs_analysis_id", table_name="analysis_jobs")
    op.drop_index("ix_analysis_jobs_user_id", table_name="analysis_jobs")
    op.drop_index("ix_analysis_jobs_project_id", table_name="analysis_jobs")
    op.drop_table("analysis_jobs")
