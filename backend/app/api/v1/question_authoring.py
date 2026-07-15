from __future__ import annotations

# ruff: noqa: E501
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import Question, QuestionBank, QuestionChoice, UserAccount
from backend.app.domain.enums import ContentStatus, UserRole
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/question-banks", tags=["question-authoring"])


class BankCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    owner_org_unit_id: UUID
    is_shared: bool = False


class ChoiceInput(BaseModel):
    content: str = Field(min_length=1)
    is_correct: bool = False


class QuestionCreate(BaseModel):
    content: str = Field(min_length=1)
    difficulty: str | None = None
    choices: list[ChoiceInput] = Field(min_length=2, max_length=10)


class BankResponse(BaseModel):
    id: UUID
    name: str
    status: str


@router.get("", response_model=list[BankResponse])
def list_banks(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN)),
    ],
) -> list[BankResponse]:
    rows = db.scalars(select(QuestionBank).order_by(QuestionBank.created_at.desc()))
    return [BankResponse.model_validate(row, from_attributes=True) for row in rows]


@router.post("", response_model=BankResponse, status_code=201)
def create_bank(
    payload: BankCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> BankResponse:
    bank = QuestionBank(
        name=payload.name,
        owner_org_unit_id=payload.owner_org_unit_id,
        is_shared=payload.is_shared,
        created_by=account.person_id,
    )
    db.add(bank)
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="question_bank.create", subject_type="question_bank", subject_id=bank.id, metadata={"name": payload.name})
    db.commit()
    db.refresh(bank)
    return BankResponse.model_validate(bank, from_attributes=True)


@router.post("/{bank_id}/questions", status_code=201)
def create_question(
    bank_id: UUID,
    payload: QuestionCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> dict[str, str]:
    bank = db.get(QuestionBank, bank_id)
    if bank is None or bank.status != ContentStatus.DRAFT:
        raise HTTPException(status_code=404, detail="Draft question bank not found")
    if sum(choice.is_correct for choice in payload.choices) != 1:
        raise HTTPException(status_code=422, detail="Exactly one choice must be correct")
    question = Question(bank_id=bank.id, content=payload.content, difficulty=payload.difficulty)
    db.add(question)
    db.flush()
    db.add_all(
        [
            QuestionChoice(
                question_id=question.id,
                content=choice.content,
                is_correct=choice.is_correct,
                base_order=index,
            )
            for index, choice in enumerate(payload.choices)
        ]
    )
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="question.create", subject_type="question", subject_id=question.id)
    db.commit()
    return {"id": str(question.id), "status": "draft"}


@router.post("/{bank_id}/publish", response_model=BankResponse)
def publish_bank(
    bank_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> BankResponse:
    bank = db.get(QuestionBank, bank_id)
    if bank is None:
        raise HTTPException(status_code=404, detail="Question bank not found")
    bank.status = ContentStatus.ACTIVE
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="question_bank.publish", subject_type="question_bank", subject_id=bank.id)
    db.commit()
    db.refresh(bank)
    return BankResponse.model_validate(bank, from_attributes=True)
