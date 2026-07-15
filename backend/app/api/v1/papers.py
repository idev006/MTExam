from __future__ import annotations

# The endpoint declarations are intentionally kept compact; domain validation remains typed.
# ruff: noqa: E501
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import ExamPaper, ExamPaperQuestion, Question, Subject, UserAccount
from backend.app.domain.enums import PaperStatus, UserRole
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/papers", tags=["papers"])


class PaperCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    org_unit_id: UUID
    question_ids: list[UUID] = Field(min_length=1, max_length=200)
    variant_count: int = Field(default=1, ge=1, le=20)
    subject_id: UUID | None = None


class PaperResponse(BaseModel):
    id: UUID
    title: str
    status: str
    question_count: int
    subject_id: UUID | None = None


@router.get("", response_model=list[PaperResponse])
def list_papers(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))],
) -> list[PaperResponse]:
    papers = list(db.scalars(select(ExamPaper).order_by(ExamPaper.created_at.desc())))
    return [PaperResponse(id=paper.id, title=paper.title, status=paper.status, question_count=len(list(db.scalars(select(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id))))) for paper in papers]


@router.post("", response_model=PaperResponse, status_code=201)
def create_paper(
    payload: PaperCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    questions = list(db.scalars(select(Question).where(Question.id.in_(payload.question_ids))))
    if len(questions) != len(set(payload.question_ids)):
        raise HTTPException(status_code=422, detail="One or more questions do not exist")
    if payload.subject_id is not None and db.get(Subject, payload.subject_id) is None:
        raise HTTPException(status_code=422, detail="Subject not found")
    paper = ExamPaper(title=payload.title, question_selection_mode="fixed_set", variant_count=payload.variant_count, status=PaperStatus.DRAFT, org_unit_id=payload.org_unit_id, subject_id=payload.subject_id, created_by=account.person_id)
    db.add(paper)
    db.flush()
    db.add_all([ExamPaperQuestion(exam_paper_id=paper.id, question_id=question.id, base_order_index=index, score_weight=question.default_score_weight) for index, question in enumerate(questions)])
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="paper.create", subject_type="exam_paper", subject_id=paper.id)
    db.commit()
    return PaperResponse(id=paper.id, title=paper.title, status=paper.status, question_count=len(questions), subject_id=paper.subject_id)


@router.post("/{paper_id}/publish", response_model=PaperResponse)
def publish_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    count = db.scalar(select(func.count()).select_from(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id)) or 0
    if count < 1:
        raise HTTPException(status_code=409, detail="Paper must contain questions")
    if paper.variant_count > 1 and paper.question_selection_mode != "fixed_set":
        raise HTTPException(status_code=409, detail="Paper selection mode is not supported")
    paper.status = PaperStatus.PUBLISHED
    paper.published_at = utc_now()
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="paper.publish", subject_type="exam_paper", subject_id=paper.id)
    db.commit()
    return PaperResponse(id=paper.id, title=paper.title, status=paper.status, question_count=count, subject_id=paper.subject_id)


@router.get("/{paper_id}/validate")
def validate_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))],
) -> dict[str, object]:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    count = db.scalar(select(func.count()).select_from(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id)) or 0
    errors = [] if count else ["paper must contain at least one question"]
    return {"paper_id": str(paper.id), "valid": not errors, "question_count": count, "errors": errors}
