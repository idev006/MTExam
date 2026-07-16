from __future__ import annotations

import hashlib

# ruff: noqa: E501
import json
import random
from datetime import date, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    ExamAnswer,
    ExamPaper,
    ExamPaperQuestion,
    ExamSession,
    ExamVariant,
    ExamVariantQuestion,
    ExamWindow,
    ExamWindowScope,
    PersonUnitAssignment,
    Question,
    QuestionChoice,
    QuestionVersion,
    UserAccount,
)
from backend.app.domain.enums import ExamSessionStatus, ExamWindowStatus, UserRole
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/exam-sessions", tags=["exam-sessions"])


class AnswerRequest(BaseModel):
    variant_question_id: UUID
    selected_choice_id: UUID


class SessionResponse(BaseModel):
    id: UUID
    exam_window_id: UUID
    status: str
    started_at: str
    ends_at: str
    submitted_at: str | None
    score: float | None
    answers: dict[str, str]
    questions: list[dict[str, object]]


@router.post("/windows/{window_id}/start", response_model=SessionResponse, status_code=201)
def start_or_resume(
    window_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE, UserRole.SUPER_ADMIN))],
) -> SessionResponse:
    window = db.get(ExamWindow, window_id)
    if window is None or window.status != ExamWindowStatus.OPEN:
        raise HTTPException(status_code=409, detail="Exam window is not open")
    existing = db.scalar(select(ExamSession).where(ExamSession.exam_window_id == window.id, ExamSession.person_id == account.person_id))
    if existing is not None:
        _expire_if_needed(existing, db)
        return _response(existing, db)
    paper = db.get(ExamPaper, window.exam_paper_id)
    if paper is None:
        raise HTTPException(status_code=409, detail="Exam paper not found")
    scope_ids = set(db.scalars(select(ExamWindowScope.org_unit_id).where(ExamWindowScope.exam_window_id == window.id)))
    if scope_ids:
        today = date.today()
        assignment = db.scalar(select(PersonUnitAssignment).where(PersonUnitAssignment.person_id == account.person_id, PersonUnitAssignment.org_unit_id.in_(scope_ids), PersonUnitAssignment.effective_from <= today, (PersonUnitAssignment.effective_to.is_(None)) | (PersonUnitAssignment.effective_to >= today)))
        if assignment is None and account.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Your organization is not allowed in this exam window")
    if window.window_open_at and window.late_entry_minutes and utc_now() > window.window_open_at + timedelta(minutes=window.late_entry_minutes):
        raise HTTPException(status_code=403, detail="Late entry period has ended")
    variant = _ensure_variant(paper, db, account.person_id)
    now = utc_now()
    ends = now + timedelta(minutes=window.duration_minutes or 60)
    if window.window_close_at:
        ends = min(ends, window.window_close_at)
    session = ExamSession(person_id=account.person_id, exam_window_id=window.id, exam_variant_id=variant.id, examinee_snapshot_text=json.dumps({"person_id": str(account.person_id)}), org_unit_id=paper.org_unit_id, started_at=now, ends_at=ends, status=ExamSessionStatus.IN_PROGRESS)
    db.add(session)
    db.flush()
    record_audit(db, actor_person_id=account.person_id, event_type="exam_session.start", subject_type="exam_session", subject_id=session.id, metadata={"window_id": str(window.id)})
    db.commit()
    return _response(session, db)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE, UserRole.SUPER_ADMIN))],
) -> SessionResponse:
    session = _owned_session(session_id, account, db)
    _expire_if_needed(session, db)
    return _response(session, db)


@router.put("/{session_id}/answers", response_model=SessionResponse)
def save_answer(
    session_id: UUID,
    payload: AnswerRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE, UserRole.SUPER_ADMIN))],
) -> SessionResponse:
    session = _owned_session(session_id, account, db)
    _expire_if_needed(session, db)
    if session.status != ExamSessionStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Exam session is no longer answerable")
    question = db.get(ExamVariantQuestion, payload.variant_question_id)
    choice = db.get(QuestionChoice, payload.selected_choice_id)
    if question is None or choice is None or choice.question_id != _question_id_from_version(question.question_version_id, db):
        raise HTTPException(status_code=422, detail="Choice does not belong to the exam question")
    now = utc_now()
    answer = db.scalar(select(ExamAnswer).where(ExamAnswer.exam_session_id == session.id, ExamAnswer.exam_variant_question_id == question.id))
    if answer is None:
        answer = ExamAnswer(exam_session_id=session.id, exam_variant_question_id=question.id, selected_choice_id=choice.id, first_answered_at=now, last_updated_at=now)
        db.add(answer)
    else:
        answer.selected_choice_id, answer.last_updated_at = choice.id, now
    db.commit()
    return _response(session, db)


@router.post("/{session_id}/submit", response_model=SessionResponse)
def submit_session(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE, UserRole.SUPER_ADMIN))],
) -> SessionResponse:
    session = _owned_session(session_id, account, db)
    _expire_if_needed(session, db)
    if session.status == ExamSessionStatus.SUBMITTED:
        return _response(session, db)
    if session.status != ExamSessionStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Exam session cannot be submitted")
    answers = list(db.scalars(select(ExamAnswer).where(ExamAnswer.exam_session_id == session.id)))
    score = 0.0
    for answer in answers:
        choice = db.get(QuestionChoice, answer.selected_choice_id)
        answer.is_correct_cache = bool(choice and choice.is_correct)
        if answer.is_correct_cache:
            variant_question = db.get(ExamVariantQuestion, answer.exam_variant_question_id)
            score += float(variant_question.score_weight if variant_question else 1)
    session.score = score
    session.status = ExamSessionStatus.SUBMITTED
    session.submitted_at = utc_now()
    record_audit(db, actor_person_id=account.person_id, event_type="exam_session.submit", subject_type="exam_session", subject_id=session.id, metadata={"score": score})
    db.commit()
    return _response(session, db)


def _owned_session(session_id: UUID, account: UserAccount, db: Session) -> ExamSession:
    session = db.get(ExamSession, session_id)
    if session is None or (session.person_id != account.person_id and account.role != UserRole.SUPER_ADMIN):
        raise HTTPException(status_code=404, detail="Exam session not found")
    return session


def _expire_if_needed(session: ExamSession, db: Session) -> None:
    if session.status == ExamSessionStatus.IN_PROGRESS and utc_now() >= session.ends_at:
        session.status = ExamSessionStatus.TIMED_OUT
        db.commit()


def _ensure_variant(paper: ExamPaper, db: Session, person_id: UUID | None = None) -> ExamVariant:
    variants = list(db.scalars(select(ExamVariant).where(ExamVariant.exam_paper_id == paper.id).order_by(ExamVariant.variant_label)))
    if not variants:
        variants = []
        paper_questions = list(db.scalars(select(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id).order_by(ExamPaperQuestion.base_order_index)))
        for variant_index in range(paper.variant_count):
            label = chr(65 + variant_index) if variant_index < 26 else f"V{variant_index + 1}"
            seed = hashlib.sha256(f"{paper.id}:{label}".encode()).hexdigest()
            variant = ExamVariant(exam_paper_id=paper.id, variant_label=label, generation_seed_reference=seed)
            db.add(variant)
            db.flush()
            ordered_questions = list(paper_questions)
            random.Random(seed).shuffle(ordered_questions)
            for index, paper_question in enumerate(ordered_questions):
                question = db.get(Question, paper_question.question_id)
                choices = list(db.scalars(select(QuestionChoice).where(QuestionChoice.question_id == question.id).order_by(QuestionChoice.base_order)))
                random.Random(f"{seed}:{question.id}").shuffle(choices)
                version = QuestionVersion(question_id=question.id, content_snapshot=question.content, explanation=question.explanation, choices_snapshot_text=json.dumps([{"id": str(choice.id), "content": choice.content, "is_correct": choice.is_correct} for choice in choices]))
                db.add(version)
                db.flush()
                db.add(ExamVariantQuestion(exam_variant_id=variant.id, question_version_id=version.id, order_index=index, choice_display_order_text=json.dumps([str(choice.id) for choice in choices]), score_weight=paper_question.score_weight))
            variants.append(variant)
        db.commit()
    if person_id is None or len(variants) == 1:
        return variants[0]
    digest = hashlib.sha256(f"{paper.id}:{person_id}".encode()).digest()
    return variants[int.from_bytes(digest[:4], "big") % len(variants)]


def _question_id_from_version(version_id: UUID, db: Session) -> UUID | None:
    version = db.get(QuestionVersion, version_id)
    return version.question_id if version else None


def _response(session: ExamSession, db: Session) -> SessionResponse:
    variant_questions = list(db.scalars(select(ExamVariantQuestion).where(ExamVariantQuestion.exam_variant_id == session.exam_variant_id).order_by(ExamVariantQuestion.order_index)))
    answers = {str(row.exam_variant_question_id): str(row.selected_choice_id) for row in db.scalars(select(ExamAnswer).where(ExamAnswer.exam_session_id == session.id))}
    questions: list[dict[str, object]] = []
    for row in variant_questions:
        version = db.get(QuestionVersion, row.question_version_id)
        snapshot = json.loads(version.choices_snapshot_text) if version else []
        item = {"id": str(row.id), "order_index": row.order_index, "content": version.content_snapshot if version else "", "choices": [{"id": choice["id"], "content": choice["content"]} for choice in snapshot]}
        if session.status == ExamSessionStatus.SUBMITTED and version:
            item["explanation"] = version.explanation
        questions.append(item)
    return SessionResponse(id=session.id, exam_window_id=session.exam_window_id, status=session.status, started_at=session.started_at.isoformat(), ends_at=session.ends_at.isoformat(), submitted_at=session.submitted_at.isoformat() if session.submitted_at else None, score=float(session.score) if session.score is not None else None, answers=answers, questions=questions)
