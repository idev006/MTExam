from __future__ import annotations

# Endpoint declarations are intentionally compact; lifecycle rules stay in named helpers.
# ruff: noqa: E501
from datetime import UTC, datetime
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
    ExamSession,
    ExamWindow,
    ExamWindowScope,
    OrgUnit,
    UserAccount,
)
from backend.app.domain.enums import (
    ExamCompletionPolicy,
    ExamSessionStatus,
    ExamWindowMode,
    ExamWindowStatus,
    PaperStatus,
    ResultVisibilityPolicy,
    UserRole,
)
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import accessible_org_unit_ids, active_org_unit_ids

router = APIRouter(prefix="/exam-windows", tags=["exam-windows"])


class WindowEligibleOrgUnit(BaseModel):
    org_unit_id: UUID
    eligible_count: int = Field(ge=0, le=1_000_000)


class WindowCreate(BaseModel):
    exam_paper_id: UUID
    title: str | None = Field(default=None, max_length=255)
    mode: ExamWindowMode = ExamWindowMode.INDIVIDUAL
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    completion_policy: ExamCompletionPolicy = ExamCompletionPolicy.FIXED_END
    result_visibility: ResultVisibilityPolicy = ResultVisibilityPolicy.IMMEDIATE
    late_entry_minutes: int = Field(default=0, ge=0, le=1440)
    eligible_org_units: list[WindowEligibleOrgUnit] = Field(default_factory=list, max_length=100)
    allowed_org_unit_ids: list[UUID] = Field(default_factory=list, max_length=100)
    window_open_at: str | None = None
    window_close_at: str | None = None


class WindowStatusUpdate(BaseModel):
    status: Literal["open", "suspended", "closed", "cancelled"]
    reason: str | None = Field(default=None, max_length=500)


class WindowResponse(BaseModel):
    id: UUID
    exam_paper_id: UUID
    paper_title: str
    title: str
    mode: str
    duration_minutes: int | None
    completion_policy: str
    result_visibility: str
    late_entry_minutes: int
    eligible_org_units: list[WindowEligibleOrgUnit] = Field(default_factory=list)
    allowed_org_unit_ids: list[UUID] = Field(default_factory=list)
    status: str
    window_open_at: str | None
    window_close_at: str | None
    session_counts: dict[str, int] = Field(default_factory=dict)
    can_manage: bool = False


class WindowClockResponse(BaseModel):
    window_id: UUID
    server_now: str
    status: str
    deadline: str | None
    remaining_seconds: int | None


@router.get("", response_model=list[WindowResponse])
def list_windows(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.EXAM_AUTHOR,
                UserRole.EXAM_COORDINATOR,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
                UserRole.EXAMINEE,
            )
        ),
    ],
) -> list[WindowResponse]:
    windows = list(db.scalars(select(ExamWindow).order_by(ExamWindow.created_at.desc())))
    visible = [window for window in windows if _can_view_window(db, account, window)]
    return [_response(window, db, account) for window in visible]


@router.post("", response_model=WindowResponse, status_code=201)
def create_window(
    payload: WindowCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.EXAM_COORDINATOR, UserRole.SUPER_ADMIN)),
    ],
) -> WindowResponse:
    paper = db.get(ExamPaper, payload.exam_paper_id)
    if paper is None or paper.status != PaperStatus.PUBLISHED:
        raise HTTPException(status_code=409, detail="Only published papers can create an exam window")
    paper_scopes = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    paper_quotas = {row.org_unit_id: row.eligible_count for row in paper_scopes}
    if paper.passing_percentage is None or not paper_quotas or any(value is None for value in paper_quotas.values()):
        raise HTTPException(status_code=409, detail="Exam Creation policy is incomplete")
    if account.role == UserRole.EXAM_COORDINATOR:
        scoped_orgs = accessible_org_unit_ids(db, account)
        paper_quotas = {
            org_id: count for org_id, count in paper_quotas.items() if org_id in scoped_orgs
        }
        if not paper_quotas:
            raise HTTPException(status_code=403, detail="Exam Creation is outside coordinator scope")
    quota_by_org = _window_quotas(payload, paper_quotas)
    if not set(quota_by_org).issubset(paper_quotas):
        raise HTTPException(status_code=422, detail="Window organizations must use the Exam Creation scope template")
    if any(count > int(paper_quotas[org_id] or 0) for org_id, count in quota_by_org.items()):
        raise HTTPException(status_code=422, detail="Window quota cannot exceed the Exam Creation template")
    open_at = _parse_datetime(payload.window_open_at)
    close_at = _parse_datetime(payload.window_close_at)
    if close_at and open_at and close_at <= open_at:
        raise HTTPException(status_code=422, detail="window_close_at must be after window_open_at")
    duration_minutes = payload.duration_minutes or paper.default_duration_minutes
    window = ExamWindow(
        exam_paper_id=paper.id,
        title=payload.title.strip() if payload.title and payload.title.strip() else f"{paper.title} - รอบสอบ",
        mode=payload.mode,
        duration_minutes=duration_minutes,
        completion_policy=payload.completion_policy,
        result_visibility=payload.result_visibility,
        late_entry_minutes=payload.late_entry_minutes,
        status=ExamWindowStatus.SCHEDULED,
        created_by=account.person_id,
        window_open_at=open_at,
        window_close_at=close_at,
    )
    db.add(window)
    db.flush()
    db.add_all(
        [
            ExamWindowScope(
                exam_window_id=window.id,
                org_unit_id=org_unit_id,
                eligible_count=eligible_count,
            )
            for org_unit_id, eligible_count in quota_by_org.items()
        ]
    )
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="exam_window.create",
        subject_type="exam_window",
        subject_id=window.id,
        metadata={
            "paper_id": str(paper.id),
            "duration_minutes": duration_minutes,
            "completion_policy": str(payload.completion_policy),
            "result_visibility": str(payload.result_visibility),
            "quota_total": sum(quota_by_org.values()),
        },
    )
    db.commit()
    db.refresh(window)
    return _response(window, db, account)


@router.patch("/{window_id}/status", response_model=WindowResponse)
def change_window_status(
    window_id: UUID,
    payload: WindowStatusUpdate,
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
) -> WindowResponse:
    window = db.get(ExamWindow, window_id)
    if window is None:
        raise HTTPException(status_code=404, detail="Exam window not found")
    _require_window_manager(account, window.created_by)
    if payload.status in {ExamWindowStatus.SUSPENDED, ExamWindowStatus.CANCELLED} and not (
        payload.reason and payload.reason.strip()
    ):
        raise HTTPException(status_code=422, detail="A reason is required to suspend or cancel an exam window")
    return _change_status(db, window=window, account=account, target=payload.status, reason=payload.reason)


@router.delete("/{window_id}")
def delete_unused_window(
    window_id: UUID,
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
) -> dict[str, str]:
    window = db.get(ExamWindow, window_id)
    if window is None:
        raise HTTPException(status_code=404, detail="Exam window not found")
    _require_window_manager(account, window.created_by)
    session_count = db.scalar(select(func.count()).select_from(ExamSession).where(ExamSession.exam_window_id == window.id)) or 0
    if window.status not in {ExamWindowStatus.SCHEDULED, ExamWindowStatus.CANCELLED} or session_count:
        raise HTTPException(status_code=409, detail="Only a Scheduled or Cancelled Exam Window without sessions can be deleted")
    paper_id = window.exam_paper_id
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="exam_window.delete",
        subject_type="exam_window",
        subject_id=window.id,
        metadata={"paper_id": str(paper_id), "status": str(window.status)},
    )
    db.execute(delete(ExamWindowScope).where(ExamWindowScope.exam_window_id == window.id))
    db.delete(window)
    db.commit()
    return {"status": "deleted", "paper_id": str(paper_id)}


@router.post("/{window_id}/open", response_model=WindowResponse)
def open_window(
    window_id: UUID,
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
) -> WindowResponse:
    """Compatibility endpoint; new clients use PATCH /status."""
    window = db.get(ExamWindow, window_id)
    if window is None:
        raise HTTPException(status_code=404, detail="Exam window not found")
    _require_window_manager(account, window.created_by)
    return _change_status(db, window=window, account=account, target=ExamWindowStatus.OPEN)


@router.get("/{window_id}/clock", response_model=WindowClockResponse)
def window_clock(
    window_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.EXAM_AUTHOR,
                UserRole.EXAM_COORDINATOR,
                UserRole.EXAMINEE,
                UserRole.VIEWER,
            )
        ),
    ],
) -> WindowClockResponse:
    window = db.get(ExamWindow, window_id)
    if window is None or not _can_view_window(db, account, window):
        raise HTTPException(status_code=404, detail="Exam window not found")
    now = datetime.now(UTC).replace(tzinfo=None)
    deadline = window.window_close_at
    if window.status == ExamWindowStatus.OPEN and deadline and now >= deadline:
        window.status = ExamWindowStatus.CLOSED
        record_audit(
            db,
            actor_person_id=None,
            event_type="exam_window.auto_close",
            subject_type="exam_window",
            subject_id=window.id,
        )
        db.commit()
    remaining = None if deadline is None else max(0, int((deadline - now).total_seconds()))
    return WindowClockResponse(
        window_id=window.id,
        server_now=now.isoformat() + "Z",
        status=window.status,
        deadline=deadline.isoformat() + "Z" if deadline else None,
        remaining_seconds=remaining,
    )


def _window_quotas(payload: WindowCreate, paper_quotas: dict[UUID, int | None]) -> dict[UUID, int]:
    if payload.eligible_org_units:
        result = {row.org_unit_id: row.eligible_count for row in payload.eligible_org_units}
        if len(result) != len(payload.eligible_org_units):
            raise HTTPException(status_code=422, detail="Window organizations must be unique")
        return result
    selected = payload.allowed_org_unit_ids or list(paper_quotas)
    if len(set(selected)) != len(selected):
        raise HTTPException(status_code=422, detail="Window organizations must be unique")
    if not set(selected).issubset(paper_quotas):
        raise HTTPException(status_code=422, detail="Window organizations must use the Exam Creation scope template")
    return {org_id: int(paper_quotas[org_id]) for org_id in selected if org_id in paper_quotas and paper_quotas[org_id] is not None}


def _change_status(
    db: Session,
    *,
    window: ExamWindow,
    account: UserAccount,
    target: str,
    reason: str | None = None,
) -> WindowResponse:
    transitions = {
        ExamWindowStatus.SCHEDULED: {ExamWindowStatus.OPEN, ExamWindowStatus.CANCELLED},
        ExamWindowStatus.OPEN: {ExamWindowStatus.SUSPENDED, ExamWindowStatus.CLOSED},
        ExamWindowStatus.SUSPENDED: {ExamWindowStatus.OPEN, ExamWindowStatus.CLOSED, ExamWindowStatus.CANCELLED},
        ExamWindowStatus.CLOSED: set(),
        ExamWindowStatus.CANCELLED: set(),
    }
    if window.status == target:
        return _response(window, db, account)
    if target not in transitions.get(window.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot change exam window from {window.status} to {target}")
    if target == ExamWindowStatus.OPEN:
        paper = db.get(ExamPaper, window.exam_paper_id)
        scopes = list(db.scalars(select(ExamWindowScope).where(ExamWindowScope.exam_window_id == window.id)))
        if paper is None or paper.status != PaperStatus.PUBLISHED or not scopes or any(row.eligible_count is None for row in scopes):
            raise HTTPException(status_code=409, detail="Published paper and complete window quotas are required")
        now = utc_now()
        if window.window_open_at and now < window.window_open_at:
            raise HTTPException(status_code=409, detail="Exam window start time has not arrived")
        if window.window_close_at and now >= window.window_close_at:
            raise HTTPException(status_code=409, detail="Exam window close time has passed")
        window.window_open_at = window.window_open_at or now
    previous = window.status
    window.status = target
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="exam_window.status_change",
        subject_type="exam_window",
        subject_id=window.id,
        metadata={"from": str(previous), "to": str(target), "reason": reason},
    )
    db.commit()
    db.refresh(window)
    return _response(window, db, account)


def _require_window_manager(account: UserAccount, owner_id: UUID) -> None:
    if account.role != UserRole.SUPER_ADMIN and owner_id != account.person_id:
        raise HTTPException(status_code=403, detail="Exam Window is outside your operation scope")


def _can_view_window(db: Session, account: UserAccount, window: ExamWindow) -> bool:
    if account.role == UserRole.SUPER_ADMIN or window.created_by == account.person_id:
        return True
    scope_ids = set(db.scalars(select(ExamWindowScope.org_unit_id).where(ExamWindowScope.exam_window_id == window.id)))
    if account.role in {
        UserRole.VIEWER,
        UserRole.DIVISION_ADMIN,
        UserRole.BUREAU_ADMIN,
        UserRole.STATION_ADMIN,
        UserRole.EXAM_COORDINATOR,
    }:
        return bool(scope_ids & accessible_org_unit_ids(db, account))
    for assigned_id in active_org_unit_ids(db, account):
        unit = db.get(OrgUnit, assigned_id)
        while unit is not None:
            if unit.id in scope_ids:
                return True
            unit = db.get(OrgUnit, unit.parent_id) if unit.parent_id else None
    return False


def _response(
    window: ExamWindow, db: Session, account: UserAccount | None = None
) -> WindowResponse:
    paper = db.get(ExamPaper, window.exam_paper_id)
    scopes = list(db.scalars(select(ExamWindowScope).where(ExamWindowScope.exam_window_id == window.id)))
    counts = {status.value: 0 for status in ExamSessionStatus}
    for status, count in db.execute(
        select(ExamSession.status, func.count()).where(ExamSession.exam_window_id == window.id).group_by(ExamSession.status)
    ):
        counts[str(status)] = int(count)
    counts["total"] = sum(counts.values())
    return WindowResponse(
        id=window.id,
        exam_paper_id=window.exam_paper_id,
        paper_title=paper.title if paper else "Exam Paper",
        title=window.title or (paper.title if paper else "Exam Window"),
        mode=window.mode,
        duration_minutes=window.duration_minutes,
        completion_policy=window.completion_policy,
        result_visibility=window.result_visibility,
        late_entry_minutes=window.late_entry_minutes,
        eligible_org_units=[
            WindowEligibleOrgUnit(org_unit_id=row.org_unit_id, eligible_count=row.eligible_count or 0)
            for row in scopes
        ],
        allowed_org_unit_ids=[row.org_unit_id for row in scopes],
        status=window.status,
        window_open_at=window.window_open_at.isoformat() if window.window_open_at else None,
        window_close_at=window.window_close_at.isoformat() if window.window_close_at else None,
        session_counts=counts,
        can_manage=(
            account is not None
            and (
                account.role == UserRole.SUPER_ADMIN
                or (
                    account.role in {UserRole.EXAM_AUTHOR, UserRole.EXAM_COORDINATOR}
                    and window.created_by == account.person_id
                )
            )
        ),
    )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).replace(tzinfo=None)
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Invalid ISO datetime") from error
