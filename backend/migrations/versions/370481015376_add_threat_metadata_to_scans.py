
"""add threat metadata to scans

Revision ID: 370481015376
Revises: a5179bb46f52
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "370481015376"
down_revision: Union[str, Sequence[str], None] = "a5179bb46f52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable columns first so existing records remain valid.
    op.add_column(
        "scans",
        sa.Column("match_type", sa.String(length=30), nullable=True)
    )

    op.add_column(
        "scans",
        sa.Column("threat_sources", sa.JSON(), nullable=True)
    )

    op.add_column(
        "scans",
        sa.Column("threat_types", sa.JSON(), nullable=True)
    )

    # Initialize metadata for existing scan records.
    op.execute(
        "UPDATE scans SET threat_sources = '[]'::json "
        "WHERE threat_sources IS NULL"
    )

    op.execute(
        "UPDATE scans SET threat_types = '[]'::json "
        "WHERE threat_types IS NULL"
    )

    # Enforce non-null constraints after backfilling.
    op.alter_column(
        "scans",
        "threat_sources",
        existing_type=sa.JSON(),
        nullable=False
    )

    op.alter_column(
        "scans",
        "threat_types",
        existing_type=sa.JSON(),
        nullable=False
    )


def downgrade() -> None:
    op.drop_column("scans", "threat_types")
    op.drop_column("scans", "threat_sources")
    op.drop_column("scans", "match_type")
