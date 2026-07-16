"""store explanation in immutable exam question snapshots"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260716_0009"
down_revision: str | Sequence[str] | None = "20260716_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("question_versions") as batch:
        batch.add_column(sa.Column("explanation", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("question_versions") as batch:
        batch.drop_column("explanation")
