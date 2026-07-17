from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.base import utc_now
from backend.app.db.models import (
    ExamAnswer,
    ExamSession,
    ExamVariantQuestion,
    QuestionChoice,
)
from backend.app.domain.enums import ExamSessionStatus


def maximum_score(db: Session, session: ExamSession) -> Decimal:
    weights = db.scalars(
        select(ExamVariantQuestion.score_weight).where(
            ExamVariantQuestion.exam_variant_id == session.exam_variant_id
        )
    )
    return sum((Decimal(weight) for weight in weights), Decimal("0"))


def finalize_session(
    db: Session,
    session: ExamSession,
    *,
    status: ExamSessionStatus,
) -> Decimal:
    """Cache correctness and score once for every terminal completion path."""
    if session.status in {
        ExamSessionStatus.SUBMITTED,
        ExamSessionStatus.TIMED_OUT,
        ExamSessionStatus.FORCE_CLOSED,
    } and session.score is not None:
        return Decimal(session.score)

    score = Decimal("0")
    answers = db.scalars(
        select(ExamAnswer).where(ExamAnswer.exam_session_id == session.id)
    )
    for answer in answers:
        choice = db.get(QuestionChoice, answer.selected_choice_id)
        answer.is_correct_cache = bool(choice and choice.is_correct)
        if answer.is_correct_cache:
            question = db.get(ExamVariantQuestion, answer.exam_variant_question_id)
            score += Decimal(question.score_weight if question else 1)
    session.score = score
    session.status = status
    session.submitted_at = session.submitted_at or utc_now()
    return score
