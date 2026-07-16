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
from backend.app.domain.enums import (
    ExamSessionStatus,
    ExamWindowStatus,
    PaperStatus,
)


class ExamPaper(Base):
    __tablename__ = "exam_papers"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subject_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    question_selection_mode: Mapped[str] = mapped_column(String(30))
    pool_criteria_text: Mapped[str | None] = mapped_column(Text)
    variant_count: Mapped[int] = mapped_column(Integer, default=1)
    desired_question_count: Mapped[int] = mapped_column(Integer, default=1)
    passing_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(30), default=PaperStatus.DRAFT, index=True)
    org_unit_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("org_units.id"), index=True)
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("persons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)


class ExamPaperOrgUnit(Base):
    __tablename__ = "exam_paper_org_units"
    __table_args__ = (UniqueConstraint("exam_paper_id", "org_unit_id", name="uq_paper_org_unit"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_paper_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_papers.id"), index=True)
    org_unit_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("org_units.id"), index=True)
    eligible_count: Mapped[int | None] = mapped_column(Integer)


class ExamPaperQuestion(Base):
    __tablename__ = "exam_paper_questions"
    __table_args__ = (UniqueConstraint("exam_paper_id", "question_id", name="uq_paper_question"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_paper_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_papers.id"), index=True)
    question_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("questions.id"))
    base_order_index: Mapped[int] = mapped_column(Integer)
    score_weight: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class ExamPaperSelectedQuestion(Base):
    __tablename__ = "exam_paper_selected_questions"
    __table_args__ = (
        UniqueConstraint("exam_paper_id", "question_id", name="uq_selected_paper_question"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_paper_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_papers.id"), index=True)
    question_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("questions.id"))
    score_weight: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class ExamVariant(Base):
    __tablename__ = "exam_variants"
    __table_args__ = (
        UniqueConstraint("exam_paper_id", "variant_label", name="uq_paper_variant_label"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_paper_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_papers.id"), index=True)
    variant_label: Mapped[str] = mapped_column(String(20))
    generation_seed_reference: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class ExamVariantQuestion(Base):
    __tablename__ = "exam_variant_questions"
    __table_args__ = (
        UniqueConstraint(
            "exam_variant_id",
            "question_version_id",
            name="uq_variant_question_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_variant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_variants.id"), index=True)
    question_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("question_versions.id"))
    order_index: Mapped[int] = mapped_column(Integer)
    choice_display_order_text: Mapped[str] = mapped_column(Text)
    score_weight: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class ExamWindow(Base):
    __tablename__ = "exam_windows"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_paper_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_papers.id"), index=True)
    mode: Mapped[str] = mapped_column(String(30))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    late_entry_minutes: Mapped[int] = mapped_column(Integer, default=0)
    window_open_at: Mapped[datetime | None] = mapped_column(DateTime)
    window_close_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(30),
        default=ExamWindowStatus.SCHEDULED,
        index=True,
    )
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("persons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class ExamWindowScope(Base):
    __tablename__ = "exam_window_scopes"
    __table_args__ = (
        UniqueConstraint("exam_window_id", "org_unit_id", name="uq_window_org_scope"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_window_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_windows.id"), index=True)
    org_unit_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("org_units.id"))


class ExamSession(Base):
    __tablename__ = "exam_sessions"
    __table_args__ = (
        UniqueConstraint("person_id", "exam_window_id", name="uq_person_exam_window"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    person_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("persons.id"), index=True)
    exam_window_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_windows.id"), index=True)
    exam_variant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_variants.id"))
    examinee_snapshot_text: Mapped[str] = mapped_column(Text)
    org_unit_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("org_units.id"), index=True)
    eligibility_org_unit_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("org_units.id"), index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(30),
        default=ExamSessionStatus.IN_PROGRESS,
        index=True,
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    __table_args__ = (
        UniqueConstraint(
            "exam_session_id",
            "exam_variant_question_id",
            name="uq_session_variant_question",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    exam_session_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("exam_sessions.id"), index=True)
    exam_variant_question_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("exam_variant_questions.id"),
    )
    selected_choice_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("question_choices.id"))
    first_answered_at: Mapped[datetime] = mapped_column(DateTime)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime)
    is_correct_cache: Mapped[bool | None] = mapped_column(Boolean)
