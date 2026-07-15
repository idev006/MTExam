from __future__ import annotations

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
from backend.app.db.models import ExamPaper, ExamWindow, UserAccount
from backend.app.domain.enums import ExamWindowMode, ExamWindowStatus, PaperStatus, UserRole

router = APIRouter(prefix="/exam-windows", tags=["exam-windows"])


class WindowCreate(BaseModel):
    exam_paper_id: UUID
    mode: ExamWindowMode = ExamWindowMode.INDIVIDUAL
    duration_minutes: int = Field(default=60, ge=1, le=600)
    window_open_at: str | None = None
    window_close_at: str | None = None


class WindowResponse(BaseModel):
    id: UUID
    exam_paper_id: UUID
    mode: str
    duration_minutes: int | None
    status: str
    window_open_at: str | None
    window_close_at: str | None


@router.get("", response_model=list[WindowResponse])
def list_windows(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.VIEWER))],
) -> list[WindowResponse]:
    return [_response(window) for window in db.scalars(select(ExamWindow).order_by(ExamWindow.created_at.desc()))]


@router.post("", response_model=WindowResponse, status_code=201)
def create_window(
    payload: WindowCreate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> WindowResponse:
    paper = db.get(ExamPaper, payload.exam_paper_id)
    if paper is None or paper.status != PaperStatus.PUBLISHED:
        raise HTTPException(status_code=409, detail="Only published papers can open an exam window")
    window = ExamWindow(exam_paper_id=paper.id, mode=payload.mode, duration_minutes=payload.duration_minutes, status=ExamWindowStatus.SCHEDULED, created_by=account.person_id)
    db.add(window)
    db.commit()
    db.refresh(window)
    return _response(window)


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
    db.refresh(window)
    return _response(window)


def _response(window: ExamWindow) -> WindowResponse:
    return WindowResponse(id=window.id, exam_paper_id=window.exam_paper_id, mode=window.mode, duration_minutes=window.duration_minutes, status=window.status, window_open_at=window.window_open_at.isoformat() if window.window_open_at else None, window_close_at=window.window_close_at.isoformat() if window.window_close_at else None)
