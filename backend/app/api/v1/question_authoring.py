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
from backend.app.db.models import Question, QuestionBank, QuestionChoice, Subject, UserAccount
from backend.app.domain.enums import ContentStatus, UserRole
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import active_org_unit_ids, can_access_org_unit

router = APIRouter(prefix="/question-banks", tags=["question-authoring"])


class BankCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    owner_org_unit_id: UUID
    is_shared: bool = False
    subject_id: UUID | None = None


class SubjectCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class SubjectResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    status: str


class ChoiceInput(BaseModel):
    content: str = Field(min_length=1)
    is_correct: bool = False


class QuestionCreate(BaseModel):
    content: str = Field(min_length=1)
    explanation: str | None = None
    difficulty: str | None = None
    choices: list[ChoiceInput] = Field(min_length=2, max_length=10)


class QuestionUpdate(QuestionCreate):
    pass


class BankResponse(BaseModel):
    id: UUID
    name: str
    status: str
    subject_id: UUID | None = None


class QuestionResponse(BaseModel):
    id: UUID
    content: str
    difficulty: str | None
    status: str
    choices: list[dict[str, object]]
    bank_id: UUID
    bank_name: str


@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN, UserRole.VIEWER)),
    ],
) -> list[SubjectResponse]:
    return [
        SubjectResponse.model_validate(row, from_attributes=True)
        for row in db.scalars(select(Subject).order_by(Subject.name))
    ]


@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(
    payload: SubjectCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
) -> SubjectResponse:
    if db.scalar(select(Subject).where(Subject.code == payload.code.strip())):
        raise HTTPException(status_code=409, detail="Subject code already exists")
    subject = Subject(
        code=payload.code.strip(), name=payload.name.strip(), description=payload.description
    )
    db.add(subject)
    db.flush()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="subject.create",
        subject_type="subject",
        subject_id=subject.id,
        metadata={"code": subject.code},
    )
    db.commit()
    db.refresh(subject)
    return SubjectResponse.model_validate(subject, from_attributes=True)


@router.get("", response_model=list[BankResponse])
def list_banks(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN)),
    ],
) -> list[BankResponse]:
    allowed = active_org_unit_ids(db, account)
    rows = db.scalars(
        select(QuestionBank)
        .where(QuestionBank.is_shared.is_(True) | QuestionBank.owner_org_unit_id.in_(allowed))
        .order_by(QuestionBank.created_at.desc())
    )
    return [BankResponse.model_validate(row, from_attributes=True) for row in rows]


@router.get("/questions", response_model=list[QuestionResponse])
def list_questions_for_selection(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
    subject_id: UUID | None = None,
) -> list[QuestionResponse]:
    query = (
        select(Question, QuestionBank)
        .join(QuestionBank, Question.bank_id == QuestionBank.id)
        .where(Question.status == ContentStatus.DRAFT)
    )
    if subject_id is not None:
        query = query.where(QuestionBank.subject_id == subject_id)
    return [
        QuestionResponse(
            id=question.id,
            content=question.content,
            difficulty=question.difficulty,
            status=question.status,
            bank_id=bank.id,
            bank_name=bank.name,
            choices=[
                {"id": str(choice.id), "content": choice.content, "is_correct": choice.is_correct}
                for choice in db.scalars(
                    select(QuestionChoice)
                    .where(QuestionChoice.question_id == question.id)
                    .order_by(QuestionChoice.base_order)
                )
            ],
        )
        for question, bank in db.execute(query).all()
    ]


@router.post("", response_model=BankResponse, status_code=201)
def create_bank(
    payload: BankCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> BankResponse:
    if not can_access_org_unit(db, account, payload.owner_org_unit_id):
        raise HTTPException(status_code=403, detail="Organization scope is not allowed")
    bank = QuestionBank(
        name=payload.name,
        owner_org_unit_id=payload.owner_org_unit_id,
        is_shared=payload.is_shared,
        subject_id=payload.subject_id,
        created_by=account.person_id,
    )
    db.add(bank)
    db.commit()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="question_bank.create",
        subject_type="question_bank",
        subject_id=bank.id,
        metadata={"name": payload.name},
    )
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
    question = Question(
        bank_id=bank.id,
        content=payload.content,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
    )
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
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="question.create",
        subject_type="question",
        subject_id=question.id,
    )
    db.commit()
    return {"id": str(question.id), "status": "draft"}


@router.get("/{bank_id}/questions", response_model=list[QuestionResponse])
def list_questions(
    bank_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
) -> list[QuestionResponse]:
    if db.get(QuestionBank, bank_id) is None:
        raise HTTPException(status_code=404, detail="Question bank not found")
    questions = db.scalars(
        select(Question).where(Question.bank_id == bank_id).order_by(Question.created_at)
    )
    return [
        QuestionResponse(
            id=question.id,
            content=question.content,
            difficulty=question.difficulty,
            status=question.status,
            bank_id=question.bank_id,
            bank_name=db.get(QuestionBank, question.bank_id).name,
            choices=[
                {"id": str(choice.id), "content": choice.content, "is_correct": choice.is_correct}
                for choice in db.scalars(
                    select(QuestionChoice)
                    .where(QuestionChoice.question_id == question.id)
                    .order_by(QuestionChoice.base_order)
                )
            ],
        )
        for question in questions
    ]


@router.post("/{bank_id}/publish", response_model=BankResponse)
def publish_bank(
    bank_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> BankResponse:
    bank = db.get(QuestionBank, bank_id)
    if bank is None:
        raise HTTPException(status_code=404, detail="Question bank not found")
    questions = list(db.scalars(select(Question).where(Question.bank_id == bank.id)))
    if not questions or any(
        not list(
            db.scalars(select(QuestionChoice).where(QuestionChoice.question_id == question.id))
        )
        for question in questions
    ):
        raise HTTPException(
            status_code=409, detail="Every published bank must contain questions with choices"
        )
    bank.status = ContentStatus.ACTIVE
    db.commit()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="question_bank.publish",
        subject_type="question_bank",
        subject_id=bank.id,
    )
    db.commit()
    db.refresh(bank)
    return BankResponse.model_validate(bank, from_attributes=True)


@router.put("/{bank_id}/questions/{question_id}")
def update_question(
    bank_id: UUID,
    question_id: UUID,
    payload: QuestionUpdate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> dict[str, str]:
    question = db.scalar(
        select(Question).where(Question.id == question_id, Question.bank_id == bank_id)
    )
    if question is None or question.status != ContentStatus.DRAFT:
        raise HTTPException(status_code=404, detail="Draft question not found")
    if sum(choice.is_correct for choice in payload.choices) != 1:
        raise HTTPException(status_code=422, detail="Exactly one choice must be correct")
    question.content, question.explanation, question.difficulty = (
        payload.content,
        payload.explanation,
        payload.difficulty,
    )
    for choice in list(
        db.scalars(select(QuestionChoice).where(QuestionChoice.question_id == question.id))
    ):
        db.delete(choice)
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
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="question.update",
        subject_type="question",
        subject_id=question.id,
    )
    db.commit()
    return {"id": str(question.id), "status": "draft"}
