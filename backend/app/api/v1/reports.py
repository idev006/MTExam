from __future__ import annotations

# ruff: noqa: E501
import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    Employee,
    ExamPaper,
    ExamSession,
    ExamVariant,
    PracticeExamSession,
    UserAccount,
)
from backend.app.domain.enums import UserRole

router = APIRouter(prefix="/reports", tags=["reports"])


class SystemReport(BaseModel):
    employee_total: int
    employee_active: int
    employee_inactive: int
    exam_in_progress: int
    exam_submitted: int
    average_score: float | None


class ExamCreationStats(BaseModel):
    paper_id: str
    title: str
    subject_id: str | None
    variant_count: int
    session_total: int
    submitted_total: int
    in_progress_total: int
    average_score: float | None


@router.get("/summary", response_model=SystemReport)
def get_summary(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER))],
    employee_status: str | None = None,
) -> SystemReport:
    employee_query = select(func.count()).select_from(Employee)
    if employee_status:
        employee_query = employee_query.where(Employee.emp_status == employee_status)
    total = db.scalar(employee_query) or 0
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


@router.get("/exam-creations", response_model=list[ExamCreationStats])
def list_exam_creation_stats(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER, UserRole.EXAM_AUTHOR))],
    subject_id: str | None = None,
) -> list[ExamCreationStats]:
    """Statistics are scoped to each ExamPaper creation, never combined globally."""
    query = select(ExamPaper).order_by(ExamPaper.created_at.desc())
    if subject_id:
        query = query.where(ExamPaper.subject_id == subject_id)
    result: list[ExamCreationStats] = []
    for paper in db.scalars(query):
        # ExamSession references a variant, and each variant references its paper.
        sessions = list(db.scalars(select(ExamSession).join(ExamVariant, ExamSession.exam_variant_id == ExamVariant.id).where(ExamVariant.exam_paper_id == paper.id)))
        submitted = [session for session in sessions if session.status == "submitted"]
        scores = [float(session.score) for session in submitted if session.score is not None]
        result.append(ExamCreationStats(paper_id=str(paper.id), title=paper.title, subject_id=str(paper.subject_id) if paper.subject_id else None, variant_count=paper.variant_count, session_total=len(sessions), submitted_total=len(submitted), in_progress_total=sum(session.status == "in_progress" for session in sessions), average_score=sum(scores) / len(scores) if scores else None))
    return result


@router.get("/employees.csv")
def export_employees_csv(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER))],
) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["emp_cid", "emp_fname", "emp_lname", "emp_position", "emp_bh", "emp_bk", "emp_kk", "emp_status"])
    for employee in db.scalars(select(Employee).order_by(Employee.emp_cid)):
        writer.writerow([employee.emp_cid, employee.emp_fname, employee.emp_lname, employee.emp_position or "", employee.emp_bh or "", employee.emp_bk or "", employee.emp_kk or "", employee.emp_status])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=employees.csv"})
