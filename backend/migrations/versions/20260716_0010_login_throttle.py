"""add persistent failed-login throttling"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260716_0010"
down_revision: str | Sequence[str] | None = "20260716_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username_normalized", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("first_failed_at", sa.DateTime(), nullable=False),
        sa.Column("last_failed_at", sa.DateTime(), nullable=False),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username_normalized", "ip_address", name="uq_login_attempt_identity"),
    )
    op.create_index(
        "ix_login_attempts_username_normalized",
        "login_attempts",
        ["username_normalized"],
    )
    op.create_index("ix_login_attempts_ip_address", "login_attempts", ["ip_address"])
    op.create_index("ix_login_attempts_locked_until", "login_attempts", ["locked_until"])


def downgrade() -> None:
    op.drop_index("ix_login_attempts_locked_until", table_name="login_attempts")
    op.drop_index("ix_login_attempts_ip_address", table_name="login_attempts")
    op.drop_index("ix_login_attempts_username_normalized", table_name="login_attempts")
    op.drop_table("login_attempts")
