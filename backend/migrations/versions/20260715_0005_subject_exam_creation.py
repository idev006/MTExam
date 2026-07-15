"""add subjects and bind question banks/papers to subjects"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0005"
down_revision: str | Sequence[str] | None = "20260715_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
        sa.UniqueConstraint("code", name=op.f("uq_subjects_code")),
    )
    op.create_index(op.f("ix_subjects_status"), "subjects", ["status"], unique=False)
    with op.batch_alter_table("question_banks") as batch:
        batch.add_column(sa.Column("subject_id", sa.Uuid(), nullable=True))
        batch.create_index(batch.f("ix_question_banks_subject_id"), ["subject_id"], unique=False)
        batch.create_foreign_key(
            batch.f("fk_question_banks_subject_id_subjects"), "subjects", ["subject_id"], ["id"]
        )
    with op.batch_alter_table("exam_papers") as batch:
        batch.add_column(sa.Column("subject_id", sa.Uuid(), nullable=True))
        batch.create_index(batch.f("ix_exam_papers_subject_id"), ["subject_id"], unique=False)
        batch.create_foreign_key(
            batch.f("fk_exam_papers_subject_id_subjects"), "subjects", ["subject_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("exam_papers") as batch:
        batch.drop_constraint("fk_exam_papers_subject_id_subjects")
        batch.drop_index(batch.f("ix_exam_papers_subject_id"))
        batch.drop_column("subject_id")
    with op.batch_alter_table("question_banks") as batch:
        batch.drop_constraint("fk_question_banks_subject_id_subjects")
        batch.drop_index(batch.f("ix_question_banks_subject_id"))
        batch.drop_column("subject_id")
    op.drop_index(op.f("ix_subjects_status"), table_name="subjects")
    op.drop_table("subjects")
