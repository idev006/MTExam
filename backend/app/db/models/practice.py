from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, utc_now


class PracticeExamSession(Base):
    """Durable anonymous practice session; replace identity link when auth is enabled."""

    __tablename__ = "practice_exam_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bank_code: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", index=True)
    answers_text: Mapped[str] = mapped_column(Text, default="{}")
    score: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
