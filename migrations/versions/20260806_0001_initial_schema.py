"""Initial Sentrix schema baseline.

Revision ID: 20260806_0001
Revises: None
Create Date: 2026-08-06
"""

from alembic import op

from database import db
import models  # noqa: F401 - registers core tables
import settings_models  # noqa: F401 - registers user settings table


revision = "20260806_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the complete current schema on an empty database.

    Existing installations should be stamped to this baseline after their
    schema has been verified, then upgraded normally for later revisions.
    """
    db.metadata.create_all(bind=op.get_bind())


def downgrade():
    """Drop the baseline schema in dependency-safe order."""
    db.metadata.drop_all(bind=op.get_bind())
