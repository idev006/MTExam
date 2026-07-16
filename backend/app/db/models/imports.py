from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, utc_now
from backend.app.domain.enums import ImportBatchStatus, ImportRowStatus


class PersonnelImportBatch(Base):
    __tablename__ = "personnel_import_batches"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    file_checksum: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    import_mode: Mapped[str] = mapped_column(String(30), default="full_snapshot")
    status: Mapped[str] = mapped_column(String(40), default=ImportBatchStatus.UPLOADED)
    uploaded_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("persons.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    added_count: Mapped[int] = mapped_column(Integer, default=0)
    changed_count: Mapped[int] = mapped_column(Integer, default=0)
    moved_count: Mapped[int] = mapped_column(Integer, default=0)
    missing_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary_text: Mapped[str | None] = mapped_column(Text)
    rollback_snapshot_text: Mapped[str | None] = mapped_column(Text)


class PersonnelImportRow(Base):
    __tablename__ = "personnel_import_rows"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    batch_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("personnel_import_batches.id"),
        index=True,
    )
    row_number: Mapped[int] = mapped_column(Integer)
    raw_data_text: Mapped[str] = mapped_column(Text)
    normalized_identifier_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    validation_status: Mapped[str] = mapped_column(
        String(30),
        default=ImportRowStatus.PENDING,
    )
    action: Mapped[str | None] = mapped_column(String(30))
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
