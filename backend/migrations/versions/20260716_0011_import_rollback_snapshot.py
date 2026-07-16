"""store personnel import rollback snapshots"""

import sqlalchemy as sa
from alembic import op

revision = "20260716_0011"
down_revision = "20260716_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "personnel_import_batches",
        sa.Column("rollback_snapshot_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("personnel_import_batches", "rollback_snapshot_text")
