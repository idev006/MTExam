"""add exam paper revision and edit audit metadata"""

import sqlalchemy as sa
from alembic import op

revision = "20260717_0015"
down_revision = "20260717_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exam_papers", sa.Column("family_id", sa.Uuid(), nullable=True))
    op.add_column(
        "exam_papers",
        sa.Column("revision_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("exam_papers", sa.Column("based_on_paper_id", sa.Uuid(), nullable=True))
    op.add_column("exam_papers", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("exam_papers", sa.Column("updated_by", sa.Uuid(), nullable=True))
    op.add_column("exam_papers", sa.Column("change_summary", sa.String(length=500), nullable=True))
    op.create_index("ix_exam_papers_family_id", "exam_papers", ["family_id"])
    op.create_index("ix_exam_papers_based_on_paper_id", "exam_papers", ["based_on_paper_id"])
    op.execute(
        "UPDATE exam_papers SET family_id = id, updated_at = created_at, "
        "updated_by = created_by WHERE family_id IS NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_exam_papers_based_on_paper_id", table_name="exam_papers")
    op.drop_index("ix_exam_papers_family_id", table_name="exam_papers")
    op.drop_column("exam_papers", "change_summary")
    op.drop_column("exam_papers", "updated_by")
    op.drop_column("exam_papers", "updated_at")
    op.drop_column("exam_papers", "based_on_paper_id")
    op.drop_column("exam_papers", "revision_number")
    op.drop_column("exam_papers", "family_id")
