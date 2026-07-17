from __future__ import annotations

# The endpoint declarations are intentionally kept compact; domain validation remains typed.
# ruff: noqa: E501
import hashlib
import json
import random
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    ExamPaper,
    ExamPaperOrgUnit,
    ExamPaperQuestion,
    ExamSession,
    ExamWindow,
    OrgUnit,
    Question,
    Subject,
    UserAccount,
)
from backend.app.domain.enums import PaperStatus, UserRole
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import (
    accessible_org_unit_ids,
    active_org_unit_ids,
)

router = APIRouter(prefix="/papers", tags=["papers"])


class PaperCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    org_unit_id: UUID
    question_ids: list[UUID] = Field(min_length=1, max_length=200)
    desired_question_count: int = Field(ge=1, le=200)
    default_duration_minutes: int = Field(default=60, ge=1, le=600)
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
    default_duration_minutes: int = 60
    allowed_org_unit_count: int = 0
    passing_percentage: float | None = None
    published_at: str | None = None
    family_id: UUID | None = None
    revision_number: int = 1
    based_on_paper_id: UUID | None = None
    change_summary: str | None = None
    window_count: int = 0
    session_count: int = 0
    can_edit: bool = False
    can_revise: bool = False


class EligibleOrgUnit(BaseModel):
    org_unit_id: UUID
    eligible_count: int = Field(ge=0, le=1_000_000)


class PaperStatusUpdate(BaseModel):
    status: Literal["draft", "published", "archived"]


class PaperUpdate(PaperCreate):
    change_summary: str = Field(min_length=3, max_length=500)


class PaperRevisionCreate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    change_summary: str = Field(min_length=3, max_length=500)


class PaperEditResponse(BaseModel):
    id: UUID
    title: str
    org_unit_id: UUID
    subject_id: UUID | None
    question_ids: list[UUID]
    desired_question_count: int
    default_duration_minutes: int
    eligible_org_units: list[EligibleOrgUnit]
    passing_percentage: float
    variant_count: int
    question_selection_mode: str
    pool_criteria: dict[str, object] | None
    change_summary: str | None


class PaperQuotaItem(BaseModel):
    org_unit_id: UUID
    org_unit_name: str
    eligible_count: int


class PaperQuotaPolicyResponse(BaseModel):
    paper_id: UUID
    default_duration_minutes: int
    eligible_org_units: list[PaperQuotaItem]


def _paper_response(
    db: Session, paper: ExamPaper, account: UserAccount | None = None
) -> PaperResponse:
    question_count = (
        db.scalar(
            select(func.count())
            .select_from(ExamPaperQuestion)
            .where(ExamPaperQuestion.exam_paper_id == paper.id)
        )
        or 0
    )
    allowed_org_unit_count = (
        db.scalar(
            select(func.count())
            .select_from(ExamPaperOrgUnit)
            .where(ExamPaperOrgUnit.exam_paper_id == paper.id)
        )
        or 0
    )
    window_count = db.scalar(select(func.count()).select_from(ExamWindow).where(ExamWindow.exam_paper_id == paper.id)) or 0
    session_count = (
        db.scalar(
            select(func.count())
            .select_from(ExamSession)
            .join(ExamWindow, ExamWindow.id == ExamSession.exam_window_id)
            .where(ExamWindow.exam_paper_id == paper.id)
        )
        or 0
    )
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        status=paper.status,
        question_count=question_count,
        subject_id=paper.subject_id,
        desired_question_count=paper.desired_question_count,
        default_duration_minutes=paper.default_duration_minutes,
        allowed_org_unit_count=allowed_org_unit_count,
        passing_percentage=(
            float(paper.passing_percentage) if paper.passing_percentage is not None else None
        ),
        published_at=paper.published_at.isoformat() if paper.published_at else None,
        family_id=paper.family_id,
        revision_number=paper.revision_number,
        based_on_paper_id=paper.based_on_paper_id,
        change_summary=paper.change_summary,
        window_count=window_count,
        session_count=session_count,
        can_edit=(
            account is not None
            and (account.role == UserRole.SUPER_ADMIN or paper.created_by == account.person_id)
            and paper.status == PaperStatus.DRAFT
            and window_count == 0
        ),
        can_revise=(
            account is not None
            and (account.role == UserRole.SUPER_ADMIN or paper.created_by == account.person_id)
        ),
    )


def _validated_payload(
    db: Session, account: UserAccount, payload: PaperCreate
) -> tuple[list[Question], list[OrgUnit], dict[UUID, int]]:
    allowed_content_orgs = accessible_org_unit_ids(db, account)
    if payload.org_unit_id not in allowed_content_orgs:
        raise HTTPException(status_code=403, detail="Paper owner organization scope is not allowed")
    if len(payload.question_ids) < payload.desired_question_count:
        raise HTTPException(status_code=422, detail="question_ids must contain at least desired_question_count items")
    quota_by_org = {item.org_unit_id: item.eligible_count for item in payload.eligible_org_units}
    if len(quota_by_org) != len(payload.eligible_org_units):
        raise HTTPException(status_code=422, detail="Eligible organizations must be unique")
    org_units = list(db.scalars(select(OrgUnit).where(OrgUnit.id.in_(quota_by_org), OrgUnit.status == "active")))
    if len(org_units) != len(quota_by_org):
        raise HTTPException(status_code=422, detail="All eligible organizations must be active")
    if any(unit.id not in allowed_content_orgs for unit in org_units):
        raise HTTPException(status_code=403, detail="One or more allowed organizations are outside your scope")
    selected_org_ids = set(quota_by_org)
    for unit in org_units:
        parent_id = unit.parent_id
        while parent_id is not None:
            if parent_id in selected_org_ids:
                raise HTTPException(status_code=422, detail="Eligible organizations cannot overlap parent and child units")
            parent = db.get(OrgUnit, parent_id)
            parent_id = parent.parent_id if parent else None
    candidate_ids = list(dict.fromkeys(payload.question_ids))
    if len(candidate_ids) < payload.desired_question_count:
        raise HTTPException(status_code=422, detail="Question pool does not contain enough unique questions")
    if payload.question_selection_mode == "random_pool":
        seed = hashlib.sha256(f"{payload.title}:{','.join(sorted(str(value) for value in candidate_ids))}".encode()).hexdigest()
        random.Random(seed).shuffle(candidate_ids)
    selected_ids = candidate_ids[: payload.desired_question_count]
    questions = list(db.scalars(select(Question).where(Question.id.in_(selected_ids))))
    if len(questions) != len(set(selected_ids)):
        raise HTTPException(status_code=422, detail="One or more questions do not exist")
    question_by_id = {question.id: question for question in questions}
    questions = [question_by_id[question_id] for question_id in selected_ids]
    if payload.subject_id is not None and db.get(Subject, payload.subject_id) is None:
        raise HTTPException(status_code=422, detail="Subject not found")
    return questions, org_units, quota_by_org


def _require_paper_owner(paper: ExamPaper, account: UserAccount) -> None:
    if account.role != UserRole.SUPER_ADMIN and paper.created_by != account.person_id:
        raise HTTPException(status_code=403, detail="Only the creator can change this Exam Creation")


def _ensure_publishable(db: Session, paper: ExamPaper) -> None:
    quotas = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    if (
        paper.passing_percentage is None
        or paper.default_duration_minutes < 1
        or not quotas
        or any(row.eligible_count is None for row in quotas)
    ):
        raise HTTPException(
            status_code=409,
            detail="Duration, reporting pass policy and organization quotas are required",
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


def _change_paper_status(
    db: Session,
    *,
    paper: ExamPaper,
    account: UserAccount,
    target_status: str,
    event_type: str = "paper.status_change",
) -> PaperResponse:
    _require_paper_owner(paper, account)
    if target_status == PaperStatus.PUBLISHED:
        _ensure_publishable(db, paper)
    if target_status == PaperStatus.DRAFT:
        window_count = (
            db.scalar(
                select(func.count())
                .select_from(ExamWindow)
                .where(ExamWindow.exam_paper_id == paper.id)
            )
            or 0
        )
        if window_count:
            raise HTTPException(
                status_code=409,
                detail="Exam Creation with an Exam Window cannot return to draft",
            )
    previous_status = paper.status
    if previous_status == target_status:
        return _paper_response(db, paper, account)
    paper.status = target_status
    if target_status == PaperStatus.PUBLISHED and paper.published_at is None:
        paper.published_at = utc_now()
    elif target_status == PaperStatus.DRAFT:
        paper.published_at = None
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type=event_type,
        subject_type="exam_paper",
        subject_id=paper.id,
        metadata={"from": str(previous_status), "to": str(target_status)},
    )
    db.commit()
    db.refresh(paper)
    return _paper_response(db, paper, account)


@router.get("", response_model=list[PaperResponse])
def list_papers(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.EXAM_AUTHOR,
                UserRole.EXAM_COORDINATOR,
                UserRole.SUPER_ADMIN,
            )
        ),
    ],
) -> list[PaperResponse]:
    papers = list(db.scalars(select(ExamPaper).order_by(ExamPaper.created_at.desc())))
    if account.role == UserRole.EXAM_COORDINATOR:
        scoped_orgs = accessible_org_unit_ids(db, account)
        scoped_paper_ids = set(
            db.scalars(
                select(ExamPaperOrgUnit.exam_paper_id).where(
                    ExamPaperOrgUnit.org_unit_id.in_(scoped_orgs)
                )
            )
        )
        visible = [
            paper
            for paper in papers
            if paper.id in scoped_paper_ids and paper.status == PaperStatus.PUBLISHED
        ]
    else:
        allowed = active_org_unit_ids(db, account)
        visible = [
            paper
            for paper in papers
            if account.role == UserRole.SUPER_ADMIN
            or paper.org_unit_id in allowed
            or paper.created_by == account.person_id
        ]
    return [_paper_response(db, paper, account) for paper in visible]


@router.post("", response_model=PaperResponse, status_code=201)
def create_paper(
    payload: PaperCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    questions, org_units, quota_by_org = _validated_payload(db, account, payload)
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
        default_duration_minutes=payload.default_duration_minutes,
        passing_percentage=payload.passing_percentage,
        status=PaperStatus.DRAFT,
        org_unit_id=payload.org_unit_id,
        subject_id=payload.subject_id,
        created_by=account.person_id,
        revision_number=1,
        updated_at=utc_now(),
        updated_by=account.person_id,
    )
    db.add(paper)
    db.flush()
    paper.family_id = paper.id
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
    return _paper_response(db, paper, account)


@router.get("/{paper_id}/edit", response_model=PaperEditResponse)
def get_paper_for_edit(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))],
) -> PaperEditResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    _require_paper_owner(paper, account)
    if paper.status != PaperStatus.DRAFT or db.scalar(select(func.count()).select_from(ExamWindow).where(ExamWindow.exam_paper_id == paper.id)):
        raise HTTPException(status_code=409, detail="Only a Draft Exam Creation without an Exam Window can be edited")
    question_ids = list(db.scalars(select(ExamPaperQuestion.question_id).where(ExamPaperQuestion.exam_paper_id == paper.id).order_by(ExamPaperQuestion.base_order_index)))
    quota_rows = list(db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id)))
    return PaperEditResponse(
        id=paper.id,
        title=paper.title,
        org_unit_id=paper.org_unit_id,
        subject_id=paper.subject_id,
        question_ids=question_ids,
        desired_question_count=paper.desired_question_count,
        default_duration_minutes=paper.default_duration_minutes,
        eligible_org_units=[EligibleOrgUnit(org_unit_id=row.org_unit_id, eligible_count=row.eligible_count or 0) for row in quota_rows],
        passing_percentage=float(paper.passing_percentage or 0),
        variant_count=paper.variant_count,
        question_selection_mode=paper.question_selection_mode,
        pool_criteria=json.loads(paper.pool_criteria_text) if paper.pool_criteria_text else None,
        change_summary=paper.change_summary,
    )


@router.patch("/{paper_id}", response_model=PaperResponse)
def update_paper(
    paper_id: UUID,
    payload: PaperUpdate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))],
) -> PaperResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    _require_paper_owner(paper, account)
    window_count = db.scalar(select(func.count()).select_from(ExamWindow).where(ExamWindow.exam_paper_id == paper.id)) or 0
    if paper.status != PaperStatus.DRAFT or window_count:
        raise HTTPException(status_code=409, detail="Only a Draft Exam Creation without an Exam Window can be edited")
    questions, org_units, quota_by_org = _validated_payload(db, account, payload)
    before = {"title": paper.title, "subject_id": str(paper.subject_id), "question_count": len(list(db.scalars(select(ExamPaperQuestion.id).where(ExamPaperQuestion.exam_paper_id == paper.id))))}
    paper.title = payload.title
    paper.org_unit_id = payload.org_unit_id
    paper.subject_id = payload.subject_id
    paper.question_selection_mode = payload.question_selection_mode
    paper.pool_criteria_text = json.dumps(payload.pool_criteria, ensure_ascii=False, sort_keys=True) if payload.pool_criteria else None
    paper.variant_count = payload.variant_count
    paper.desired_question_count = payload.desired_question_count
    paper.default_duration_minutes = payload.default_duration_minutes
    paper.passing_percentage = payload.passing_percentage
    paper.updated_at = utc_now()
    paper.updated_by = account.person_id
    paper.change_summary = payload.change_summary
    db.execute(delete(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == paper.id))
    db.execute(delete(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    db.add_all([ExamPaperQuestion(exam_paper_id=paper.id, question_id=question.id, base_order_index=index, score_weight=question.default_score_weight) for index, question in enumerate(questions)])
    db.add_all([ExamPaperOrgUnit(exam_paper_id=paper.id, org_unit_id=unit.id, eligible_count=quota_by_org[unit.id]) for unit in org_units])
    record_audit(db, actor_person_id=account.person_id, event_type="paper.edit", subject_type="exam_paper", subject_id=paper.id, metadata={"before": before, "change_summary": payload.change_summary})
    db.commit()
    db.refresh(paper)
    return _paper_response(db, paper, account)


@router.post("/{paper_id}/revisions", response_model=PaperResponse, status_code=201)
def create_paper_revision(
    paper_id: UUID,
    payload: PaperRevisionCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR, UserRole.SUPER_ADMIN))],
) -> PaperResponse:
    source = db.get(ExamPaper, paper_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    _require_paper_owner(source, account)
    family_id = source.family_id or source.id
    revision_number = (db.scalar(select(func.max(ExamPaper.revision_number)).where(ExamPaper.family_id == family_id)) or source.revision_number) + 1
    revision = ExamPaper(
        title=payload.title or f"{source.title} (Revision {revision_number})",
        subject_id=source.subject_id,
        question_selection_mode=source.question_selection_mode,
        pool_criteria_text=source.pool_criteria_text,
        variant_count=source.variant_count,
        desired_question_count=source.desired_question_count,
        default_duration_minutes=source.default_duration_minutes,
        passing_percentage=source.passing_percentage,
        family_id=family_id,
        revision_number=revision_number,
        based_on_paper_id=source.id,
        updated_at=utc_now(),
        updated_by=account.person_id,
        change_summary=payload.change_summary,
        status=PaperStatus.DRAFT,
        org_unit_id=source.org_unit_id,
        created_by=account.person_id,
    )
    db.add(revision)
    db.flush()
    question_rows = list(db.scalars(select(ExamPaperQuestion).where(ExamPaperQuestion.exam_paper_id == source.id).order_by(ExamPaperQuestion.base_order_index)))
    quota_rows = list(db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == source.id)))
    db.add_all([ExamPaperQuestion(exam_paper_id=revision.id, question_id=row.question_id, base_order_index=row.base_order_index, score_weight=row.score_weight) for row in question_rows])
    db.add_all([ExamPaperOrgUnit(exam_paper_id=revision.id, org_unit_id=row.org_unit_id, eligible_count=row.eligible_count) for row in quota_rows])
    record_audit(db, actor_person_id=account.person_id, event_type="paper.revision_create", subject_type="exam_paper", subject_id=revision.id, metadata={"based_on_paper_id": str(source.id), "revision_number": revision_number, "change_summary": payload.change_summary})
    db.commit()
    db.refresh(revision)
    return _paper_response(db, revision, account)


@router.post("/{paper_id}/publish", response_model=PaperResponse)
def publish_paper(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return _change_paper_status(
        db,
        paper=paper,
        account=account,
        target_status=PaperStatus.PUBLISHED,
        event_type="paper.publish",
    )


@router.patch("/{paper_id}/status", response_model=PaperResponse)
def change_paper_status(
    paper_id: UUID,
    payload: PaperStatusUpdate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> PaperResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return _change_paper_status(
        db,
        paper=paper,
        account=account,
        target_status=payload.status,
    )


@router.get("/{paper_id}/quota-policy", response_model=PaperQuotaPolicyResponse)
def paper_quota_policy(
    paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.EXAM_AUTHOR,
                UserRole.EXAM_COORDINATOR,
                UserRole.SUPER_ADMIN,
            )
        ),
    ],
) -> PaperQuotaPolicyResponse:
    paper = db.get(ExamPaper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    rows = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    if account.role == UserRole.EXAM_COORDINATOR:
        if paper.status != PaperStatus.PUBLISHED:
            raise HTTPException(status_code=409, detail="Only published papers can schedule an Exam Window")
        scoped_orgs = accessible_org_unit_ids(db, account)
        rows = [row for row in rows if row.org_unit_id in scoped_orgs]
        if not rows:
            raise HTTPException(status_code=403, detail="Exam Creation is outside coordinator scope")
    else:
        _require_paper_owner(paper, account)
    items = []
    for row in rows:
        unit = db.get(OrgUnit, row.org_unit_id)
        if unit is not None and row.eligible_count is not None:
            items.append(
                PaperQuotaItem(
                    org_unit_id=row.org_unit_id,
                    org_unit_name=unit.name,
                    eligible_count=row.eligible_count,
                )
            )
    return PaperQuotaPolicyResponse(
        paper_id=paper.id,
        default_duration_minutes=paper.default_duration_minutes,
        eligible_org_units=items,
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
