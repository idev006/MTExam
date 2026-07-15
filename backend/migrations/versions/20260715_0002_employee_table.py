"""add employee current-state table

Revision ID: 20260715_0002
Revises: 20260715_0001
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260715_0002"
down_revision: str | Sequence[str] | None = "20260715_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the source-aligned employee master."""
    op.create_table(
        "employee",
        sa.Column("emp_cid", sa.String(length=13), nullable=False),
        sa.Column("emp_yod", sa.String(length=100), nullable=True),
        sa.Column("emp_fname", sa.String(length=150), nullable=False),
        sa.Column("emp_lname", sa.String(length=150), nullable=False),
        sa.Column("emp_position", sa.String(length=255), nullable=True),
        sa.Column("emp_position_rank", sa.Integer(), nullable=True),
        sa.Column("emp_yod_rank", sa.Integer(), nullable=True),
        sa.Column("emp_gender", sa.String(length=20), nullable=True),
        sa.Column("emp_tel", sa.String(length=20), nullable=True),
        sa.Column("emp_bh", sa.String(length=255), nullable=True),
        sa.Column("emp_bk", sa.String(length=255), nullable=True),
        sa.Column("emp_kk", sa.String(length=255), nullable=True),
        sa.Column("emp_status", sa.String(length=30), nullable=False),
        sa.Column("emp_descr", sa.Text(), nullable=True),
        sa.Column("created_dt", sa.DateTime(), nullable=False),
        sa.Column("updated_dt", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "emp_position_rank IS NULL OR emp_position_rank >= 0",
            name=op.f("ck_employee_emp_position_rank_nonnegative"),
        ),
        sa.CheckConstraint(
            "emp_yod_rank IS NULL OR emp_yod_rank >= 0",
            name=op.f("ck_employee_emp_yod_rank_nonnegative"),
        ),
        sa.PrimaryKeyConstraint("emp_cid", name=op.f("pk_employee")),
    )
    with op.batch_alter_table("employee", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_employee_emp_status"),
            ["emp_status"],
            unique=False,
        )
        batch_op.create_index(
            "ix_employee_org_path",
            ["emp_bh", "emp_bk", "emp_kk"],
            unique=False,
        )


def downgrade() -> None:
    """Remove the employee master."""
    with op.batch_alter_table("employee", schema=None) as batch_op:
        batch_op.drop_index("ix_employee_org_path")
        batch_op.drop_index(batch_op.f("ix_employee_emp_status"))

    op.drop_table("employee")
