"""Initial Sentrix schema.

Revision ID: 20260805_01
Revises:
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa

revision = "20260805_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("profile_picture", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("project_path", sa.String(length=500), nullable=False),
        sa.Column("upload_date", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_projects_project_id", "projects", ["project_id"])
    op.create_index("ix_projects_upload_date", "projects", ["upload_date"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("pylint_score", sa.Float(), nullable=False),
        sa.Column("security_count", sa.Integer(), nullable=False),
        sa.Column("formatting_status", sa.String(length=30), nullable=False),
        sa.Column("complexity", sa.String(length=30), nullable=False),
        sa.Column("analysis_duration", sa.Float(), nullable=False),
        sa.Column("total_files", sa.Integer(), nullable=False),
        sa.Column("total_lines", sa.Integer(), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("pylint_output", sa.Text(), nullable=True),
        sa.Column("bandit_output", sa.Text(), nullable=True),
        sa.Column("radon_output", sa.Text(), nullable=True),
        sa.Column("issues_count", sa.Integer(), nullable=False),
        sa.Column("functions_count", sa.Integer(), nullable=False),
        sa.Column("classes_count", sa.Integer(), nullable=False),
        sa.Column("comments_count", sa.Integer(), nullable=False),
        sa.Column("blank_lines", sa.Integer(), nullable=False),
        sa.Column("report_path", sa.String(length=255), nullable=True),
        sa.Column("syntax_output", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_analyses_project_id", "analyses", ["project_id"])
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"])
    op.create_index("ix_analyses_created_at", "analyses", ["created_at"])


def downgrade():
    op.drop_index("ix_analyses_created_at", table_name="analyses")
    op.drop_index("ix_analyses_user_id", table_name="analyses")
    op.drop_index("ix_analyses_project_id", table_name="analyses")
    op.drop_table("analyses")
    op.drop_table("reviews")
    op.drop_index("ix_projects_upload_date", table_name="projects")
    op.drop_index("ix_projects_project_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
