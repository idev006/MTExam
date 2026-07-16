"""add default duration to exam creations"""

import sqlalchemy as sa
from alembic import op

revision = "20260717_0013"
down_revision = "20260716_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "exam_papers",
        sa.Column(
            "default_duration_minutes",
            sa.Integer(),
            nullable=False,
            server_default="60",
        ),
    )


def downgrade() -> None:
    op.drop_column("exam_papers", "default_duration_minutes")
