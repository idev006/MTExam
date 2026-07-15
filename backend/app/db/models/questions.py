from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, utc_now
from backend.app.domain.enums import ContentStatus


class QuestionBank(Base):
    __tablename__ = "question_banks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subject_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("subjects.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    owner_org_unit_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("org_units.id"), index=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default=ContentStatus.DRAFT)
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("persons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default=ContentStatus.ACTIVE, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    bank_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("question_banks.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str | None] = mapped_column(String(30), index=True)
    default_score_weight: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    status: Mapped[str] = mapped_column(String(30), default=ContentStatus.DRAFT, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class QuestionChoice(Base):
    __tablename__ = "question_choices"
    __table_args__ = (
        UniqueConstraint("question_id", "base_order", name="uq_question_choice_base_order"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("questions.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    base_order: Mapped[int] = mapped_column(Integer)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name_normalized: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))


class QuestionTag(Base):
    __tablename__ = "question_tags"

    question_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("questions.id"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("tags.id"), primary_key=True)


class QuestionVersion(Base):
    __tablename__ = "question_versions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("questions.id"), index=True)
    content_snapshot: Mapped[str] = mapped_column(Text)
    choices_snapshot_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
