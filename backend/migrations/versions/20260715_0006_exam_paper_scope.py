"""add desired question count and allowed organization units to exam creations"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0006"
down_revision: str | Sequence[str] | None = "20260715_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("exam_papers") as batch:
        batch.add_column(
            sa.Column("desired_question_count", sa.Integer(), nullable=False, server_default="1")
        )
    op.create_table(
        "exam_paper_org_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("exam_paper_id", sa.Uuid(), nullable=False),
        sa.Column("org_unit_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exam_paper_id"], ["exam_papers.id"], name=op.f("fk_paper_org_unit_paper")
        ),
        sa.ForeignKeyConstraint(
            ["org_unit_id"], ["org_units.id"], name=op.f("fk_paper_org_unit_org_unit")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_paper_org_units")),
        sa.UniqueConstraint("exam_paper_id", "org_unit_id", name="uq_paper_org_unit"),
    )
    op.create_index(
        op.f("ix_exam_paper_org_units_exam_paper_id"), "exam_paper_org_units", ["exam_paper_id"]
    )
    op.create_index(
        op.f("ix_exam_paper_org_units_org_unit_id"), "exam_paper_org_units", ["org_unit_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_exam_paper_org_units_org_unit_id"), table_name="exam_paper_org_units")
    op.drop_index(op.f("ix_exam_paper_org_units_exam_paper_id"), table_name="exam_paper_org_units")
    op.drop_table("exam_paper_org_units")
    with op.batch_alter_table("exam_papers") as batch:
        batch.drop_column("desired_question_count")
