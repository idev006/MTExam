from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Path as RoutePath
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.config import PROJECT_ROOT
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import UserAccount
from backend.app.db.models.practice import PracticeExamSession
from backend.app.domain.enums import UserRole
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    topic: str
    content: str
    choices: list[str]
    correct_index: int
    explanation: str


class PracticeBank(BaseModel):
    bank_code: str
    title: str
    language: str
    version: int
    questions: list[PracticeQuestion]


class PracticeSessionResponse(BaseModel):
    session_id: UUID
    bank_code: str
    status: str
    answers: dict[int, int]
    score: int | None = None
    updated_at: datetime


class AnswerRequest(BaseModel):
    question_index: int
    choice_index: int


@lru_cache(maxsize=4)
def _load_bank(bank_code: str) -> PracticeBank:
    if bank_code != "pdpa-50":
        raise FileNotFoundError
    source = PROJECT_ROOT / "data" / "question_banks" / "pdpa_50.json"
    return PracticeBank.model_validate(json.loads(source.read_text(encoding="utf-8")))


@router.get("/banks/{bank_code}", response_model=PracticeBank)
def get_practice_bank(
    bank_code: Annotated[str, RoutePath(pattern=r"^[a-z0-9-]+$", max_length=50)],
) -> PracticeBank:
    try:
        return _load_bank(bank_code)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=404, detail="Practice question bank not found") from error


def _session_response(entity: PracticeExamSession) -> PracticeSessionResponse:
    return PracticeSessionResponse(
        session_id=entity.id,
        bank_code=entity.bank_code,
        status=entity.status,
        answers={int(k): int(v) for k, v in json.loads(entity.answers_text).items()},
        score=entity.score,
        updated_at=entity.updated_at or entity.created_at,
    )


@router.post(
    "/sessions",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_practice_session(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE))],
) -> PracticeSessionResponse:
    entity = PracticeExamSession(bank_code="pdpa-50")
    db.add(entity)
    db.commit()
    db.refresh(entity)
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="practice_session.create",
        subject_type="practice_exam_session",
        subject_id=entity.id,
    )
    db.commit()
    return _session_response(entity)


@router.get("/sessions/{session_id}", response_model=PracticeSessionResponse)
def get_practice_session(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE))],
) -> PracticeSessionResponse:
    entity = db.get(PracticeExamSession, session_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    return _session_response(entity)


@router.put("/sessions/{session_id}/answers", response_model=PracticeSessionResponse)
def save_practice_answer(
    session_id: UUID,
    request: AnswerRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE))],
) -> PracticeSessionResponse:
    entity = db.get(PracticeExamSession, session_id)
    if entity is None or entity.status != "in_progress":
        raise HTTPException(status_code=409, detail="Practice session is not writable")
    bank = _load_bank(entity.bank_code)
    valid_question = 0 <= request.question_index < len(bank.questions)
    valid_choice = valid_question and 0 <= request.choice_index < len(
        bank.questions[request.question_index].choices
    )
    if not valid_choice:
        raise HTTPException(status_code=422, detail="Answer is outside the question bank")
    answers = json.loads(entity.answers_text)
    answers[str(request.question_index)] = request.choice_index
    entity.answers_text = json.dumps(answers, separators=(",", ":"))
    entity.updated_at = utc_now()
    db.commit()
    db.refresh(entity)
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="practice_session.answer",
        subject_type="practice_exam_session",
        subject_id=entity.id,
        metadata={"question_index": request.question_index},
    )
    db.commit()
    return _session_response(entity)


@router.post("/sessions/{session_id}/submit", response_model=PracticeSessionResponse)
def submit_practice_session(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE))],
) -> PracticeSessionResponse:
    entity = db.get(PracticeExamSession, session_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    if entity.status == "submitted":
        return _session_response(entity)
    bank = _load_bank(entity.bank_code)
    answers = json.loads(entity.answers_text)
    if len(answers) != len(bank.questions):
        raise HTTPException(status_code=409, detail="Answer every question before submitting")
    entity.score = sum(
        int(int(answers[str(index)]) == question.correct_index)
        for index, question in enumerate(bank.questions)
    )
    entity.status = "submitted"
    entity.submitted_at = utc_now()
    entity.updated_at = entity.submitted_at
    db.commit()
    db.refresh(entity)
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="practice_session.submit",
        subject_type="practice_exam_session",
        subject_id=entity.id,
        metadata={"score": entity.score},
    )
    db.commit()
    return _session_response(entity)
