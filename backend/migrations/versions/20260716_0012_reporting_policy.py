"""add reporting pass policy, organization quota and quota snapshot"""

import sqlalchemy as sa
from alembic import op

revision = "20260716_0012"
down_revision = "20260716_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "exam_papers",
        sa.Column("passing_percentage", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "exam_paper_org_units",
        sa.Column("eligible_count", sa.Integer(), nullable=True),
    )
    with op.batch_alter_table("exam_sessions") as batch:
        batch.add_column(sa.Column("eligibility_org_unit_id", sa.Uuid(), nullable=True))
        batch.create_index("ix_exam_sessions_eligibility_org_unit_id", ["eligibility_org_unit_id"])
        batch.create_foreign_key(
            "fk_exam_sessions_eligibility_org_unit_id_org_units",
            "org_units",
            ["eligibility_org_unit_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("exam_sessions") as batch:
        batch.drop_constraint(
            "fk_exam_sessions_eligibility_org_unit_id_org_units", type_="foreignkey"
        )
        batch.drop_index("ix_exam_sessions_eligibility_org_unit_id")
        batch.drop_column("eligibility_org_unit_id")
    op.drop_column("exam_paper_org_units", "eligible_count")
    op.drop_column("exam_papers", "passing_percentage")
