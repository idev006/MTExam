"""add durable practice exam recovery sessions"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0004"
down_revision: str | Sequence[str] | None = "20260715_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "practice_exam_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bank_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("answers_text", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_practice_exam_sessions")),
    )
    with op.batch_alter_table("practice_exam_sessions") as batch_op:
        batch_op.create_index(batch_op.f("ix_practice_exam_sessions_bank_code"), ["bank_code"])
        batch_op.create_index(batch_op.f("ix_practice_exam_sessions_status"), ["status"])


def downgrade() -> None:
    with op.batch_alter_table("practice_exam_sessions") as batch_op:
        batch_op.drop_index(batch_op.f("ix_practice_exam_sessions_status"))
        batch_op.drop_index(batch_op.f("ix_practice_exam_sessions_bank_code"))
    op.drop_table("practice_exam_sessions")
