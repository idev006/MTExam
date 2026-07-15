from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, utc_now
from backend.app.domain.enums import ActiveStatus


class Employee(Base):
    """Current employee master imported from the approved source contract."""

    __tablename__ = "employee"
    __table_args__ = (
        CheckConstraint(
            "emp_position_rank IS NULL OR emp_position_rank >= 0",
            name="emp_position_rank_nonnegative",
        ),
        CheckConstraint(
            "emp_yod_rank IS NULL OR emp_yod_rank >= 0",
            name="emp_yod_rank_nonnegative",
        ),
        Index("ix_employee_org_path", "emp_bh", "emp_bk", "emp_kk"),
    )

    emp_cid: Mapped[str] = mapped_column(String(13), primary_key=True)
    emp_yod: Mapped[str | None] = mapped_column(String(100))
    emp_fname: Mapped[str] = mapped_column(String(150))
    emp_lname: Mapped[str] = mapped_column(String(150))
    emp_position: Mapped[str | None] = mapped_column(String(255))
    emp_position_rank: Mapped[int | None] = mapped_column(Integer)
    emp_yod_rank: Mapped[int | None] = mapped_column(Integer)
    emp_gender: Mapped[str | None] = mapped_column(String(20))
    emp_tel: Mapped[str | None] = mapped_column(String(20))
    emp_bh: Mapped[str | None] = mapped_column(String(255))
    emp_bk: Mapped[str | None] = mapped_column(String(255))
    emp_kk: Mapped[str | None] = mapped_column(String(255))
    emp_status: Mapped[str] = mapped_column(
        String(30),
        default=ActiveStatus.ACTIVE,
        index=True,
    )
    emp_descr: Mapped[str | None] = mapped_column(Text)
    created_dt: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_dt: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=lambda: utc_now() + timedelta(microseconds=1),
    )
