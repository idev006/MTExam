from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import Employee, PracticeExamSession, UserAccount
from backend.app.domain.enums import UserRole

router = APIRouter(prefix="/reports", tags=["reports"])


class SystemReport(BaseModel):
    employee_total: int
    employee_active: int
    employee_inactive: int
    exam_in_progress: int
    exam_submitted: int
    average_score: float | None


@router.get("/summary", response_model=SystemReport)
def get_summary(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER))],
) -> SystemReport:
    total = db.scalar(select(func.count()).select_from(Employee)) or 0
    active = db.scalar(
        select(func.count()).select_from(Employee).where(Employee.emp_status == "active")
    ) or 0
    submitted = db.scalar(
        select(func.count())
        .select_from(PracticeExamSession)
        .where(PracticeExamSession.status == "submitted")
    ) or 0
    in_progress = db.scalar(
        select(func.count())
        .select_from(PracticeExamSession)
        .where(PracticeExamSession.status == "in_progress")
    ) or 0
    average = db.scalar(
        select(func.avg(PracticeExamSession.score)).where(
            PracticeExamSession.status == "submitted"
        )
    )
    return SystemReport(
        employee_total=total,
        employee_active=active,
        employee_inactive=total - active,
        exam_in_progress=in_progress,
        exam_submitted=submitted,
        average_score=float(average) if average is not None else None,
    )
