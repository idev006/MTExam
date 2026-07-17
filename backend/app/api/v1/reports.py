from __future__ import annotations

# ruff: noqa: E501
import csv
import io
import zipfile
from datetime import date
from pathlib import Path
from typing import Annotated
from uuid import UUID
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
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
    OrgUnit,
    PracticeExamSession,
    UserAccount,
)
from backend.app.domain.enums import UserRole
from backend.app.schemas.reporting import (
    PersonReportDetail,
    PersonReportRow,
    QuestionAnalytics,
    ReportContext,
    ReportDashboard,
)
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import accessible_org_unit_ids
from backend.app.services.reporting import (
    ReportFilters,
    build_dashboard,
    own_results,
    person_detail,
    question_analytics,
    report_context,
)

router = APIRouter(prefix="/reports", tags=["reports"])

REPORT_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.VIEWER,
    UserRole.DIVISION_ADMIN,
    UserRole.BUREAU_ADMIN,
    UserRole.STATION_ADMIN,
    UserRole.EXAM_AUTHOR,
    UserRole.EXAM_COORDINATOR,
    UserRole.EXAMINEE,
)


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


class OrganizationStats(BaseModel):
    org_unit_id: str
    org_unit_name: str
    session_total: int
    submitted_total: int
    average_score: float | None


def _xlsx_from_rows(rows: list[list[object]], sheet_name: str = "Report") -> bytes:
    """Create a small dependency-free XLSX workbook for operational exports."""
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row):
            column = ""
            number = column_index + 1
            while number:
                number, remainder = divmod(number - 1, 26)
                column = chr(65 + remainder) + column
            text = escape("" if value is None else str(value))
            cells.append(f'<c r="{column}{row_index}" t="inlineStr"><is><t>{text}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">' + "".join(cells) + "</row>")
    sheet = (
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="'
        + escape(sheet_name)
        + '" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    workbook_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return output.getvalue()


def _filters(
    subject_id: UUID | None,
    exam_paper_id: UUID | None,
    exam_window_id: UUID | None,
    date_from: date | None,
    date_to: date | None,
    org_unit_id: UUID | None,
    page: int,
    page_size: int,
) -> ReportFilters:
    return ReportFilters(
        subject_id=subject_id,
        exam_paper_id=exam_paper_id,
        exam_window_id=exam_window_id,
        date_from=date_from,
        date_to=date_to,
        org_unit_id=org_unit_id,
        page=page,
        page_size=page_size,
    )


@router.get("/context", response_model=ReportContext)
def get_report_context(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(*REPORT_ROLES))],
) -> ReportContext:
    return report_context(db, account)


@router.get("/dashboard", response_model=ReportDashboard)
def get_report_dashboard(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(*REPORT_ROLES))],
    subject_id: UUID | None = None,
    exam_paper_id: UUID | None = None,
    exam_window_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    org_unit_id: UUID | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> ReportDashboard:
    return build_dashboard(
        db,
        account,
        _filters(
            subject_id,
            exam_paper_id,
            exam_window_id,
            date_from,
            date_to,
            org_unit_id,
            page,
            page_size,
        ),
    )


@router.get("/people/{session_id}", response_model=PersonReportDetail)
def get_person_report(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(*REPORT_ROLES))],
) -> PersonReportDetail:
    detail = person_detail(db, account, session_id)
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="report.person_detail.view",
        subject_type="exam_session",
        subject_id=session_id,
    )
    db.commit()
    return detail


@router.get("/my-results", response_model=list[PersonReportRow])
def get_my_results(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAMINEE))],
) -> list[PersonReportRow]:
    return own_results(db, account)


@router.get("/question-analytics", response_model=QuestionAnalytics)
def get_question_analytics(
    exam_paper_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.EXAM_AUTHOR))],
) -> QuestionAnalytics:
    return question_analytics(db, account, exam_paper_id)


@router.get("/export")
def export_filtered_report(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(*REPORT_ROLES))],
    format: Annotated[str, Query(pattern="^(pdf|xlsx|csv)$")],
    subject_id: UUID | None = None,
    exam_paper_id: UUID | None = None,
    exam_window_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    org_unit_id: UUID | None = None,
) -> Response:
    report = build_dashboard(
        db,
        account,
        _filters(
            subject_id,
            exam_paper_id,
            exam_window_id,
            date_from,
            date_to,
            org_unit_id,
            1,
            1_000_000,
        ),
    )
    rows: list[list[object]] = [["Name", "Organization", "Status", "Score", "Score %", "Pass"]]
    rows.extend(
        [
            [
                row.full_name,
                row.org_unit_name,
                row.status,
                row.score,
                row.score_percentage,
                row.passed,
            ]
            for row in report.people.items
        ]
    )
    stamp = date.today().isoformat()
    filename = f"mtexam-report-{report.exam_paper_id or 'empty'}-{stamp}.{format}"
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="report.export",
        subject_type="exam_paper",
        subject_id=UUID(report.exam_paper_id) if report.exam_paper_id else None,
        metadata={
            "format": format,
            "filters": {
                "exam_window_id": str(exam_window_id) if exam_window_id else None,
                "org_unit_id": str(org_unit_id) if org_unit_id else None,
            },
        },
    )
    db.commit()
    if format == "csv":
        output = io.StringIO()
        csv.writer(output).writerows(rows)
        return Response(
            content=("\ufeff" + output.getvalue()).encode("utf-8"),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    if format == "xlsx":
        return Response(
            content=_xlsx_from_rows(rows, "Report"),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    return _filtered_pdf(report, filename)


def _filtered_pdf(report: ReportDashboard, filename: str) -> Response:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    font_path = Path(__file__).parents[2] / "assets" / "fonts" / "ChakraPetch-Regular.ttf"
    pdfmetrics.registerFont(TTFont("ChakraPetch", font_path))
    font = "ChakraPetch"
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("MTExam filtered report")
    pdf.setFont(font, 14)
    pdf.drawString(40, 805, "รายงานผลการสอบ MTExam")
    pdf.setFont(font, 9)
    y = 780
    for row in report.people.items:
        pdf.drawString(
            40,
            y,
            f"{row.full_name} | {row.org_unit_name} | {row.status} | {row.score_percentage if row.score_percentage is not None else '-'}%",
        )
        y -= 15
        if y < 45:
            pdf.showPage()
            pdf.setFont(font, 9)
            y = 805
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/summary", response_model=SystemReport)
def get_summary(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
    employee_status: str | None = None,
) -> SystemReport:
    employee_query = select(func.count()).select_from(Employee)
    if employee_status:
        employee_query = employee_query.where(Employee.emp_status == employee_status)
    total = db.scalar(employee_query) or 0
    active = (
        db.scalar(select(func.count()).select_from(Employee).where(Employee.emp_status == "active"))
        or 0
    )
    exam_scope = [ExamSession.status == "submitted"]
    progress_scope = [ExamSession.status == "in_progress"]
    if account.role != UserRole.SUPER_ADMIN:
        allowed = accessible_org_unit_ids(db, account)
        exam_scope.append(ExamSession.org_unit_id.in_(allowed))
        progress_scope.append(ExamSession.org_unit_id.in_(allowed))
    practice_submitted = (
        db.scalar(
            select(func.count())
            .select_from(PracticeExamSession)
            .where(PracticeExamSession.status == "submitted")
        )
        or 0
    )
    practice_in_progress = (
        db.scalar(
            select(func.count())
            .select_from(PracticeExamSession)
            .where(PracticeExamSession.status == "in_progress")
        )
        or 0
    )
    if account.role != UserRole.SUPER_ADMIN:
        practice_submitted = practice_in_progress = 0
    submitted = (
        db.scalar(select(func.count()).select_from(ExamSession).where(*exam_scope)) or 0
    ) + practice_submitted
    in_progress = (
        db.scalar(select(func.count()).select_from(ExamSession).where(*progress_scope)) or 0
    ) + practice_in_progress
    real_avg = db.scalar(select(func.avg(ExamSession.score)).where(*exam_scope))
    practice_avg = (
        db.scalar(
            select(func.avg(PracticeExamSession.score)).where(
                PracticeExamSession.status == "submitted"
            )
        )
        if account.role == UserRole.SUPER_ADMIN
        else None
    )
    average = real_avg if real_avg is not None else practice_avg
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
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.EXAM_AUTHOR,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
    subject_id: str | None = None,
) -> list[ExamCreationStats]:
    """Statistics are scoped to each ExamPaper creation, never combined globally."""
    query = select(ExamPaper).order_by(ExamPaper.created_at.desc())
    if account.role != UserRole.SUPER_ADMIN:
        query = query.where(ExamPaper.org_unit_id.in_(accessible_org_unit_ids(db, account)))
    if subject_id:
        query = query.where(ExamPaper.subject_id == subject_id)
    result: list[ExamCreationStats] = []
    for paper in db.scalars(query):
        # ExamSession references a variant, and each variant references its paper.
        sessions = list(
            db.scalars(
                select(ExamSession)
                .join(ExamVariant, ExamSession.exam_variant_id == ExamVariant.id)
                .where(ExamVariant.exam_paper_id == paper.id)
            )
        )
        submitted = [session for session in sessions if session.status == "submitted"]
        scores = [float(session.score) for session in submitted if session.score is not None]
        result.append(
            ExamCreationStats(
                paper_id=str(paper.id),
                title=paper.title,
                subject_id=str(paper.subject_id) if paper.subject_id else None,
                variant_count=paper.variant_count,
                session_total=len(sessions),
                submitted_total=len(submitted),
                in_progress_total=sum(session.status == "in_progress" for session in sessions),
                average_score=sum(scores) / len(scores) if scores else None,
            )
        )
    return result


@router.get("/organizations", response_model=list[OrganizationStats])
def list_organization_stats(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
) -> list[OrganizationStats]:
    allowed = accessible_org_unit_ids(db, account)
    units = {unit.id: unit for unit in db.scalars(select(OrgUnit).where(OrgUnit.id.in_(allowed)))}
    sessions = list(db.scalars(select(ExamSession).where(ExamSession.org_unit_id.in_(allowed))))
    result: list[OrganizationStats] = []
    for org_id, unit in units.items():
        scoped = [session for session in sessions if session.org_unit_id == org_id]
        submitted = [session for session in scoped if session.status == "submitted"]
        scores = [float(session.score) for session in submitted if session.score is not None]
        result.append(
            OrganizationStats(
                org_unit_id=str(org_id),
                org_unit_name=unit.name,
                session_total=len(scoped),
                submitted_total=len(submitted),
                average_score=sum(scores) / len(scores) if scores else None,
            )
        )
    return sorted(result, key=lambda item: item.org_unit_name)


@router.get("/employees.csv")
def export_employees_csv(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "emp_cid",
            "emp_fname",
            "emp_lname",
            "emp_position",
            "emp_bh",
            "emp_bk",
            "emp_kk",
            "emp_status",
        ]
    )
    employees = list(db.scalars(select(Employee).order_by(Employee.emp_cid)))
    if account.role != UserRole.SUPER_ADMIN:
        allowed_ids = accessible_org_unit_ids(db, account)
        units = list(db.scalars(select(OrgUnit).where(OrgUnit.id.in_(allowed_ids))))
        names = {value for unit in units for value in (unit.name, unit.code)}
        employees = [
            employee
            for employee in employees
            if employee.emp_bk in names or employee.emp_kk in names
        ]
    for employee in employees:
        writer.writerow(
            [
                employee.emp_cid,
                employee.emp_fname,
                employee.emp_lname,
                employee.emp_position or "",
                employee.emp_bh or "",
                employee.emp_bk or "",
                employee.emp_kk or "",
                employee.emp_status,
            ]
        )
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"},
    )


@router.get("/summary.pdf")
def export_summary_pdf(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
) -> Response:
    """Export the system summary as a compact PDF; Excel can be added without changing the report model."""
    report = get_summary(db, account)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as error:
        raise RuntimeError("PDF export requires reportlab; install requirements.txt") from error
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("MTExam system summary")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(48, 800, "MTExam System Summary")
    pdf.setFont("Helvetica", 11)
    lines = [
        f"Employee total: {report.employee_total}",
        f"Employee active: {report.employee_active}",
        f"Employee inactive: {report.employee_inactive}",
        f"Exam in progress: {report.exam_in_progress}",
        f"Exam submitted: {report.exam_submitted}",
        f"Average score: {report.average_score if report.average_score is not None else '-'}",
    ]
    for index, line in enumerate(lines):
        pdf.drawString(60, 760 - index * 22, line)
    pdf.showPage()
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=mtexam-summary.pdf"},
    )


@router.get("/summary.xlsx")
def export_summary_xlsx(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
) -> Response:
    report = get_summary(db, account)
    content = _xlsx_from_rows(
        [
            ["Metric", "Value"],
            ["Employee total", report.employee_total],
            ["Employee active", report.employee_active],
            ["Employee inactive", report.employee_inactive],
            ["Exam in progress", report.exam_in_progress],
            ["Exam submitted", report.exam_submitted],
            ["Average score", report.average_score],
        ],
        "Summary",
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=mtexam-summary.xlsx"},
    )


@router.get("/exam-sessions.xlsx")
def export_exam_sessions_xlsx(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER))],
    status: str | None = None,
    org_unit_id: str | None = None,
) -> Response:
    query = select(ExamSession).order_by(ExamSession.started_at.desc())
    if status:
        query = query.where(ExamSession.status == status)
    if account.role != UserRole.SUPER_ADMIN:
        query = query.where(ExamSession.org_unit_id.in_(accessible_org_unit_ids(db, account)))
    if org_unit_id:
        query = query.where(ExamSession.org_unit_id == org_unit_id)
    rows: list[list[object]] = [
        ["session_id", "person_id", "org_unit_id", "status", "score", "started_at", "submitted_at"]
    ]
    for session in db.scalars(query):
        rows.append(
            [
                str(session.id),
                str(session.person_id),
                str(session.org_unit_id),
                session.status,
                session.score,
                session.started_at.isoformat(),
                session.submitted_at.isoformat() if session.submitted_at else "",
            ]
        )
    content = _xlsx_from_rows(rows, "ExamSessions")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=mtexam-exam-sessions.xlsx"},
    )


@router.get("/exam-sessions.pdf")
def export_exam_sessions_pdf(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.VIEWER,
                UserRole.DIVISION_ADMIN,
                UserRole.BUREAU_ADMIN,
                UserRole.STATION_ADMIN,
            )
        ),
    ],
    status: str | None = None,
) -> Response:
    query = select(ExamSession).order_by(ExamSession.started_at.desc())
    if status:
        query = query.where(ExamSession.status == status)
    if account.role != UserRole.SUPER_ADMIN:
        query = query.where(ExamSession.org_unit_id.in_(accessible_org_unit_ids(db, account)))
    sessions = list(db.scalars(query))
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as error:
        raise RuntimeError("PDF export requires reportlab; install requirements.txt") from error
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("MTExam exam sessions")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, 800, "MTExam Exam Session Report")
    pdf.setFont("Helvetica", 9)
    y = 775
    for session in sessions:
        line = f"{str(session.id)[:8]} | {session.status} | score={session.score or '-'} | {session.started_at.isoformat()}"
        pdf.drawString(40, y, line[:115])
        y -= 14
        if y < 45:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = 800
    pdf.showPage()
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=mtexam-exam-sessions.pdf"},
    )
