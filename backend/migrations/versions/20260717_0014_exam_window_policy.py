"""add exam window quota, timing policy and lifecycle metadata"""

import sqlalchemy as sa
from alembic import op

revision = "20260717_0014"
down_revision = "20260717_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("exam_windows", sa.Column("title", sa.String(length=255), nullable=True))
    op.add_column(
        "exam_windows",
        sa.Column(
            "completion_policy",
            sa.String(length=30),
            nullable=False,
            server_default="fixed_end",
        ),
    )
    op.add_column(
        "exam_window_scopes",
        sa.Column("eligible_count", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE exam_windows
        SET title = (
            SELECT exam_papers.title FROM exam_papers
            WHERE exam_papers.id = exam_windows.exam_paper_id
        )
        WHERE title IS NULL
        """
    )
    op.execute(
        """
        UPDATE exam_window_scopes
        SET eligible_count = (
            SELECT exam_paper_org_units.eligible_count
            FROM exam_paper_org_units
            JOIN exam_windows
              ON exam_windows.exam_paper_id = exam_paper_org_units.exam_paper_id
            WHERE exam_windows.id = exam_window_scopes.exam_window_id
              AND exam_paper_org_units.org_unit_id = exam_window_scopes.org_unit_id
        )
        WHERE eligible_count IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("exam_window_scopes", "eligible_count")
    op.drop_column("exam_windows", "completion_policy")
    op.drop_column("exam_windows", "title")
