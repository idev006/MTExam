"""add configurable late entry grace period to exam windows"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260716_0007"
down_revision: str | Sequence[str] | None = "20260715_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("exam_windows") as batch:
        batch.add_column(
            sa.Column("late_entry_minutes", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("exam_windows") as batch:
        batch.drop_column("late_entry_minutes")
