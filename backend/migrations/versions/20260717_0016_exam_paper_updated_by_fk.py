"""add exam paper updated-by foreign key"""

from alembic import op

revision = "20260717_0016"
down_revision = "20260717_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("exam_papers") as batch:
        batch.create_foreign_key(
            "fk_exam_papers_updated_by_persons",
            "persons",
            ["updated_by"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("exam_papers") as batch:
        batch.drop_constraint(
            "fk_exam_papers_updated_by_persons",
            type_="foreignkey",
        )
