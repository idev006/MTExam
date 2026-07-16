from __future__ import annotations

from datetime import UTC, datetime

# ruff: noqa: E501
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    ExamPaper,
    ExamPaperOrgUnit,
    ExamWindow,
    ExamWindowScope,
    UserAccount,
)
from backend.app.domain.enums import ExamWindowMode, ExamWindowStatus, PaperStatus, UserRole
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import active_org_unit_ids

router = APIRouter(prefix="/exam-windows", tags=["exam-windows"])


class WindowCreate(BaseModel):
    exam_paper_id: UUID
    mode: ExamWindowMode = ExamWindowMode.INDIVIDUAL
    duration_minutes: int = Field(default=60, ge=1, le=600)
    late_entry_minutes: int = Field(default=0, ge=0, le=1440)
    allowed_org_unit_ids: list[UUID] = Field(default_factory=list)
    window_open_at: str | None = None
    window_close_at: str | None = None


class WindowResponse(BaseModel):
    id: UUID
    exam_paper_id: UUID
    mode: str
    duration_minutes: int | None
    late_entry_minutes: int
    allowed_org_unit_ids: list[UUID] = Field(default_factory=list)
    status: str
    window_open_at: str | None
    window_close_at: str | None


class WindowClockResponse(BaseModel):
    window_id: UUID
    server_now: str
    status: str
    deadline: str | None
    remaining_seconds: int | None


@router.get("", response_model=list[WindowResponse])
def list_windows(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.VIEWER, UserRole.EXAMINEE
            )
        ),
    ],
) -> list[WindowResponse]:
    windows = list(db.scalars(select(ExamWindow).order_by(ExamWindow.created_at.desc())))
    if _account.role != UserRole.SUPER_ADMIN:
        allowed = active_org_unit_ids(db, _account)
        windows = [
            window
            for window in windows
            if set(
                db.scalars(
                    select(ExamWindowScope.org_unit_id).where(
                        ExamWindowScope.exam_window_id == window.id
                    )
                )
            )
            & allowed
        ]
    return [_response(window, db) for window in windows]


@router.post("", response_model=WindowResponse, status_code=201)
def create_window(
    payload: WindowCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> WindowResponse:
    paper = db.get(ExamPaper, payload.exam_paper_id)
    if paper is None or paper.status != PaperStatus.PUBLISHED:
        raise HTTPException(status_code=409, detail="Only published papers can open an exam window")
    if account.role != UserRole.SUPER_ADMIN and paper.created_by != account.person_id:
        raise HTTPException(status_code=403, detail="Exam Creation is outside your author scope")
    paper_scopes = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    if (
        paper.passing_percentage is None
        or not paper_scopes
        or any(row.eligible_count is None for row in paper_scopes)
    ):
        raise HTTPException(status_code=409, detail="Reporting policy is incomplete")
    close_at = _parse_datetime(payload.window_close_at)
    open_at = _parse_datetime(payload.window_open_at)
    if close_at and open_at and close_at <= open_at:
        raise HTTPException(status_code=422, detail="window_close_at must be after window_open_at")
    configured_ids = {row.org_unit_id for row in paper_scopes}
    allowed = payload.allowed_org_unit_ids or list(configured_ids)
    if not set(allowed).issubset(configured_ids):
        raise HTTPException(status_code=422, detail="Window organizations must use paper quotas")
    window = ExamWindow(
        exam_paper_id=paper.id,
        mode=payload.mode,
        duration_minutes=payload.duration_minutes,
        late_entry_minutes=payload.late_entry_minutes,
        status=ExamWindowStatus.SCHEDULED,
        created_by=account.person_id,
        window_open_at=open_at,
        window_close_at=close_at,
    )
    db.add(window)
    db.flush()
    db.add_all(
        [ExamWindowScope(exam_window_id=window.id, org_unit_id=unit_id) for unit_id in allowed]
    )
    db.commit()
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="exam_window.create",
        subject_type="exam_window",
        subject_id=window.id,
        metadata={"paper_id": str(paper.id), "duration_minutes": payload.duration_minutes},
    )
    db.commit()
    db.refresh(window)
    return _response(window, db)


@router.post("/{window_id}/open", response_model=WindowResponse)
def open_window(
    window_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> WindowResponse:
    window = db.get(ExamWindow, window_id)
    if window is None:
        raise HTTPException(status_code=404, detail="Exam window not found")
    window.status = ExamWindowStatus.OPEN
    window.window_open_at = window.window_open_at or utc_now()
    db.commit()
    record_audit(
        db,
        actor_person_id=_account.person_id,
        event_type="exam_window.open",
        subject_type="exam_window",
        subject_id=window.id,
    )
    db.commit()
    db.refresh(window)
    return _response(window, db)


@router.get("/{window_id}/clock", response_model=WindowClockResponse)
def window_clock(
    window_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.EXAMINEE, UserRole.VIEWER
            )
        ),
    ],
) -> WindowClockResponse:
    """Return a server-authoritative clock; close an expired open window atomically."""
    window = db.get(ExamWindow, window_id)
    if window is None:
        raise HTTPException(status_code=404, detail="Exam window not found")
    now = datetime.now(UTC).replace(tzinfo=None)
    deadline = window.window_close_at
    if window.status == ExamWindowStatus.OPEN and deadline and now >= deadline:
        window.status = ExamWindowStatus.CLOSED
        db.commit()
    remaining = None if deadline is None else max(0, int((deadline - now).total_seconds()))
    return WindowClockResponse(
        window_id=window.id,
        server_now=now.isoformat() + "Z",
        status=window.status,
        deadline=deadline.isoformat() + "Z" if deadline else None,
        remaining_seconds=remaining,
    )


def _response(window: ExamWindow, db: Session) -> WindowResponse:
    allowed = list(
        db.scalars(
            select(ExamWindowScope.org_unit_id).where(ExamWindowScope.exam_window_id == window.id)
        )
    )
    return WindowResponse(
        id=window.id,
        exam_paper_id=window.exam_paper_id,
        mode=window.mode,
        duration_minutes=window.duration_minutes,
        status=window.status,
        late_entry_minutes=window.late_entry_minutes,
        allowed_org_unit_ids=allowed,
        window_open_at=window.window_open_at.isoformat() if window.window_open_at else None,
        window_close_at=window.window_close_at.isoformat() if window.window_close_at else None,
    )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Invalid ISO datetime") from error
