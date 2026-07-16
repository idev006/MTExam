from __future__ import annotations

# The endpoint declarations are intentionally kept compact; domain validation remains typed.
# ruff: noqa: E501
import hashlib
import json
import random
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    ExamPaper,
    ExamPaperOrgUnit,
    ExamPaperQuestion,
    OrgUnit,
    Question,
    Subject,
    UserAccount,
)
from backend.app.domain.enums import PaperStatus, UserRole
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import active_org_unit_ids, can_access_org_unit

router = APIRouter(prefix="/papers", tags=["papers"])


class PaperCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    org_unit_id: UUID
    question_ids: list[UUID] = Field(min_length=1, max_length=200)
    desired_question_count: int = Field(ge=1, le=200)
    eligible_org_units: list[EligibleOrgUnit] = Field(min_length=1, max_length=100)
    passing_percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    variant_count: int = Field(default=1, ge=1, le=20)
    subject_id: UUID | None = None
    question_selection_mode: str = Field(default="fixed_set", pattern="^(fixed_set|random_pool)$")
    pool_criteria: dict[str, object] | None = None


class PaperResponse(BaseModel):
    id: UUID
    title: str
    status: str
    question_count: int
    subject_id: UUID | None = None
    desired_question_count: int = 1
    allowed_org_unit_count: int = 0
    passing_percentage: float | None = None


class EligibleOrgUnit(BaseModel):
    org_unit_id: UUID
    eligible_count: int = Field(ge=0, le=1_000_000)


@router.get("", response_model=list[PaperResponse])
def list_papers(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
) -> list[PaperResponse]:
    papers = list(db.scalars(select(ExamPaper).order_by(ExamPaper.created_at.desc())))
    allowed = active_org_unit_ids(db, account)
    visible = [
        paper
        for paper in papers
        if paper.org_unit_id in allowed or paper.created_by == account.person_id
    ]
    return [
        PaperResponse(
            id=paper.id,
            title=paper.title,
            status=paper.status,
            question_count=len(
                list(
                    db.scalars(
                        select(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id)
                    )
                )
            ),
        )
        for paper in visible
    ]


@router.post("", response_model=PaperResponse, status_code=201)
def create_paper(
    payload: PaperCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    if not can_access_org_unit(db, account, payload.org_unit_id):
        raise HTTPException(status_code=403, detail="Paper owner organization scope is not allowed")
    if len(payload.question_ids) < payload.desired_question_count:
        raise HTTPException(
            status_code=422,
            detail="question_ids must contain at least desired_question_count items",
        )
    quota_by_org = {item.org_unit_id: item.eligible_count for item in payload.eligible_org_units}
    if len(quota_by_org) != len(payload.eligible_org_units):
        raise HTTPException(status_code=422, detail="Eligible organizations must be unique")
    org_units = list(
        db.scalars(select(OrgUnit).where(OrgUnit.id.in_(quota_by_org), OrgUnit.status == "active"))
    )
    if len(org_units) != len(quota_by_org):
        raise HTTPException(status_code=422, detail="All eligible organizations must be active")
    if any(not can_access_org_unit(db, account, unit.id) for unit in org_units):
        raise HTTPException(
            status_code=403, detail="One or more allowed organizations are outside your scope"
        )
    selected_org_ids = set(quota_by_org)
    for unit in org_units:
        parent_id = unit.parent_id
        while parent_id is not None:
            if parent_id in selected_org_ids:
                raise HTTPException(
                    status_code=422,
                    detail="Eligible organizations cannot overlap parent and child units",
                )
            parent = db.get(OrgUnit, parent_id)
            parent_id = parent.parent_id if parent else None
    candidate_ids = list(dict.fromkeys(payload.question_ids))
    if len(candidate_ids) < payload.desired_question_count:
        raise HTTPException(
            status_code=422, detail="Question pool does not contain enough unique questions"
        )
    if payload.question_selection_mode == "random_pool":
        seed = hashlib.sha256(
            f"{payload.title}:{','.join(sorted(str(value) for value in candidate_ids))}".encode()
        ).hexdigest()
        random.Random(seed).shuffle(candidate_ids)
    selected_ids = candidate_ids[: payload.desired_question_count]
    questions = list(db.scalars(select(Question).where(Question.id.in_(selected_ids))))
    if len(questions) != len(set(selected_ids)):
        raise HTTPException(status_code=422, detail="One or more questions do not exist")
    if payload.subject_id is not None and db.get(Subject, payload.subject_id) is None:
        raise HTTPException(status_code=422, detail="Subject not found")
    paper = ExamPaper(
        title=payload.title,
        question_selection_mode=payload.question_selection_mode,
        pool_criteria_text=(
            json.dumps(payload.pool_criteria, ensure_ascii=False, sort_keys=True)
            if payload.pool_criteria
            else None
        ),
        variant_count=payload.variant_count,
        desired_question_count=payload.desired_question_count,
        passing_percentage=payload.passing_percentage,
        status=PaperStatus.DRAFT,
        org_unit_id=payload.org_unit_id,
        subject_id=payload.subject_id,
        created_by=account.person_id,
    )
    db.add(paper)
    db.flush()
    db.add_all(
        [
            ExamPaperQuestion(
                exam_paper_id=paper.id,
                question_id=question.id,
                base_order_index=index,
                score_weight=question.default_score_weight,
            )
            for index, question in enumerate(questions)
        ]
    )
    db.add_all(
        [
            ExamPaperOrgUnit(
                exam_paper_id=paper.id,
                org_unit_id=org_unit.id,
                eligible_count=quota_by_org[org_unit.id],
            )
            for org_unit in org_units
        ]
    )
    db.commit()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="paper.create",
        subject_type="exam_paper",
        subject_id=paper.id,
    )
    db.commit()
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        status=paper.status,
        question_count=len(questions),
        subject_id=paper.subject_id,
        desired_question_count=paper.desired_question_count,
        allowed_org_unit_count=len(org_units),
        passing_percentage=float(paper.passing_percentage),
    )


@router.post("/{paper_id}/publish", response_model=PaperResponse)
def publish_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    if account.role != UserRole.SUPER_ADMIN and paper.created_by != account.person_id:
        raise HTTPException(status_code=403, detail="Only the creator can publish this paper")
    quotas = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    if (
        paper.passing_percentage is None
        or not quotas
        or any(row.eligible_count is None for row in quotas)
    ):
        raise HTTPException(
            status_code=409,
            detail="Reporting pass policy and organization quotas are required",
        )
    count = (
        db.scalar(
            select(func.count())
            .select_from(ExamPaperQuestion)
            .where(ExamPaperQuestion.exam_paper_id == paper.id)
        )
        or 0
    )
    if count < 1:
        raise HTTPException(status_code=409, detail="Paper must contain questions")
    paper.status = PaperStatus.PUBLISHED
    paper.published_at = utc_now()
    db.commit()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="paper.publish",
        subject_type="exam_paper",
        subject_id=paper.id,
    )
    db.commit()
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        status=paper.status,
        question_count=count,
        subject_id=paper.subject_id,
        passing_percentage=float(paper.passing_percentage),
    )


@router.get("/{paper_id}/validate")
def validate_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
) -> dict[str, object]:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    count = (
        db.scalar(
            select(func.count())
            .select_from(ExamPaperQuestion)
            .where(ExamPaperQuestion.exam_paper_id == paper.id)
        )
        or 0
    )
    errors = [] if count else ["paper must contain at least one question"]
    return {
        "paper_id": str(paper.id),
        "valid": not errors,
        "question_count": count,
        "errors": errors,
    }


@router.get("/{paper_id}/preview")
def preview_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))
    ],
) -> dict[str, object]:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    if (
        account.role != UserRole.SUPER_ADMIN
        and paper.org_unit_id not in active_org_unit_ids(db, account)
        and paper.created_by != account.person_id
    ):
        raise HTTPException(status_code=403, detail="Paper is outside your organization scope")
    rows = list(
        db.scalars(
            select(ExamPaperQuestion)
            .where(ExamPaperQuestion.exam_paper_id == paper.id)
            .order_by(ExamPaperQuestion.base_order_index)
        )
    )
    questions = []
    for row in rows:
        question = db.get(Question, row.question_id)
        if question is not None:
            questions.append(
                {
                    "id": str(question.id),
                    "order_index": row.base_order_index,
                    "content": question.content,
                    "difficulty": question.difficulty,
                    "score_weight": float(row.score_weight),
                }
            )
    return {
        "paper_id": str(paper.id),
        "title": paper.title,
        "status": paper.status,
        "variant_count": paper.variant_count,
        "desired_question_count": paper.desired_question_count,
        "questions": questions,
    }
