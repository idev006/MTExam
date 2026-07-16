"""Scoped reporting queries shared by JSON dashboards and file exports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.base import utc_now
from backend.app.db.models import (
    ExamAnswer,
    ExamPaper,
    ExamPaperOrgUnit,
    ExamSession,
    ExamVariant,
    ExamVariantQuestion,
    ExamWindow,
    ExamWindowScope,
    OrgUnit,
    Person,
    QuestionVersion,
    Subject,
    UserAccount,
)
from backend.app.domain.enums import UserRole
from backend.app.domain.report_rules import not_started_count, pass_outcome, score_percentage
from backend.app.schemas.reporting import (
    OrganizationReportRow,
    PaginatedPeople,
    PersonReportDetail,
    PersonReportRow,
    QuestionAnalytics,
    QuestionAnalyticsRow,
    ReportContext,
    ReportDashboard,
    ReportKpis,
    ReportOption,
    ReportQuestionDetail,
    ReportSeriesItem,
)
from backend.app.services.org_authorization import (
    accessible_org_unit_ids,
    active_org_unit_ids,
)


@dataclass(frozen=True)
class ReportFilters:
    subject_id: UUID | None = None
    exam_paper_id: UUID | None = None
    exam_window_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    org_unit_id: UUID | None = None
    page: int = 1
    page_size: int = 25


def _descendants(db: Session, root_id: UUID) -> set[UUID]:
    units = list(db.scalars(select(OrgUnit).where(OrgUnit.status == "active")))
    children: dict[UUID | None, list[UUID]] = {}
    for unit in units:
        children.setdefault(unit.parent_id, []).append(unit.id)
    result = {root_id}
    queue = [root_id]
    while queue:
        for child_id in children.get(queue.pop(), []):
            if child_id not in result:
                result.add(child_id)
                queue.append(child_id)
    return result


def _visible_papers(db: Session, account: UserAccount) -> list[ExamPaper]:
    papers = list(db.scalars(select(ExamPaper).order_by(ExamPaper.created_at.desc())))
    if account.role == UserRole.SUPER_ADMIN:
        return papers
    active = active_org_unit_ids(db, account)
    scoped = accessible_org_unit_ids(db, account)
    if account.role == UserRole.EXAM_AUTHOR:
        return [p for p in papers if p.created_by == account.person_id or p.org_unit_id in active]
    if account.role == UserRole.EXAMINEE:
        own_paper_ids = set(
            db.scalars(
                select(ExamVariant.exam_paper_id)
                .join(ExamSession, ExamSession.exam_variant_id == ExamVariant.id)
                .where(ExamSession.person_id == account.person_id)
            )
        )
        window_paper_ids = set(
            db.scalars(
                select(ExamWindow.exam_paper_id)
                .join(ExamWindowScope, ExamWindowScope.exam_window_id == ExamWindow.id)
                .where(ExamWindowScope.org_unit_id.in_(active))
            )
        )
        return [p for p in papers if p.id in own_paper_ids | window_paper_ids]
    paper_ids = {
        quota.exam_paper_id
        for quota in db.scalars(select(ExamPaperOrgUnit))
        if quota.org_unit_id in scoped or bool(_descendants(db, quota.org_unit_id) & scoped)
    }
    return [p for p in papers if p.id in paper_ids]


def report_context(db: Session, account: UserAccount) -> ReportContext:
    papers = _visible_papers(db, account)
    paper_ids = {paper.id for paper in papers}
    subject_ids = {paper.subject_id for paper in papers if paper.subject_id}
    subjects = list(db.scalars(select(Subject).where(Subject.id.in_(subject_ids))))
    windows = (
        list(
            db.scalars(
                select(ExamWindow)
                .where(ExamWindow.exam_paper_id.in_(paper_ids))
                .order_by(ExamWindow.created_at.desc())
            )
        )
        if paper_ids
        else []
    )
    org_ids: set[UUID]
    if account.role == UserRole.SUPER_ADMIN:
        org_ids = accessible_org_unit_ids(db, account)
    elif account.role == UserRole.EXAMINEE:
        org_ids = active_org_unit_ids(db, account)
    else:
        org_ids = accessible_org_unit_ids(db, account)
    organizations = (
        list(db.scalars(select(OrgUnit).where(OrgUnit.id.in_(org_ids)).order_by(OrgUnit.name)))
        if org_ids
        else []
    )
    return ReportContext(
        subjects=[
            ReportOption(id=str(row.id), label=f"{row.code} — {row.name}") for row in subjects
        ],
        exam_creations=[ReportOption(id=str(row.id), label=row.title) for row in papers],
        exam_windows=[
            ReportOption(
                id=str(row.id),
                label=(
                    f"{next((p.title for p in papers if p.id == row.exam_paper_id), 'Exam')}"
                    f" · {row.status}"
                ),
                parent_id=str(row.exam_paper_id),
            )
            for row in windows
        ],
        organizations=[
            ReportOption(
                id=str(row.id),
                label=row.name,
                parent_id=str(row.parent_id) if row.parent_id else None,
            )
            for row in organizations
        ],
        default_exam_paper_id=str(papers[0].id) if papers else None,
        role=account.role,
    )


def _score_percentage(db: Session, session: ExamSession) -> float | None:
    maximum = db.scalar(
        select(func.sum(ExamVariantQuestion.score_weight)).where(
            ExamVariantQuestion.exam_variant_id == session.exam_variant_id
        )
    )
    return score_percentage(
        Decimal(session.score) if session.score is not None else None,
        Decimal(maximum) if maximum is not None else None,
    )


def _validate_filters(filters: ReportFilters) -> None:
    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise HTTPException(status_code=422, detail="date_from must not be after date_to")


def _selected_paper(db: Session, account: UserAccount, filters: ReportFilters) -> ExamPaper | None:
    papers = _visible_papers(db, account)
    if filters.subject_id:
        papers = [paper for paper in papers if paper.subject_id == filters.subject_id]
    if filters.exam_paper_id:
        paper = db.get(ExamPaper, filters.exam_paper_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="Exam Creation not found")
        if paper.id not in {row.id for row in papers}:
            raise HTTPException(status_code=403, detail="Exam Creation is outside report scope")
        return paper
    return papers[0] if papers else None


def build_dashboard(db: Session, account: UserAccount, filters: ReportFilters) -> ReportDashboard:
    _validate_filters(filters)
    paper = _selected_paper(db, account, filters)
    if paper is None:
        return _empty_dashboard(filters)
    windows = list(db.scalars(select(ExamWindow).where(ExamWindow.exam_paper_id == paper.id)))
    if filters.exam_window_id:
        windows = [window for window in windows if window.id == filters.exam_window_id]
        if not windows:
            raise HTTPException(status_code=403, detail="Exam Window is outside report scope")
    if filters.date_from:
        start = datetime.combine(filters.date_from, time.min)
        windows = [w for w in windows if (w.window_open_at or w.created_at) >= start]
    if filters.date_to:
        end = datetime.combine(filters.date_to, time.max)
        windows = [w for w in windows if (w.window_open_at or w.created_at) <= end]
    window_ids = {window.id for window in windows}
    sessions = (
        list(db.scalars(select(ExamSession).where(ExamSession.exam_window_id.in_(window_ids))))
        if window_ids
        else []
    )
    if account.role == UserRole.EXAMINEE:
        sessions = [row for row in sessions if row.person_id == account.person_id]
    allowed_orgs = accessible_org_unit_ids(db, account)
    if account.role not in (UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.EXAMINEE):
        sessions = [row for row in sessions if row.org_unit_id in allowed_orgs]
    selected_orgs: set[UUID] | None = None
    if filters.org_unit_id:
        if filters.org_unit_id not in allowed_orgs and account.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Organization is outside report scope")
        selected_orgs = _descendants(db, filters.org_unit_id)
        sessions = [row for row in sessions if row.org_unit_id in selected_orgs]
    quota_rows = list(
        db.scalars(select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id))
    )
    if account.role == UserRole.EXAMINEE:
        quota_rows = []
    elif account.role not in (UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR):
        quota_rows = [row for row in quota_rows if row.org_unit_id in allowed_orgs]
    if selected_orgs is not None:
        quota_rows = [row for row in quota_rows if row.org_unit_id in selected_orgs]
    eligible = (
        None
        if not quota_rows or any(row.eligible_count is None for row in quota_rows)
        else sum((row.eligible_count or 0) for row in quota_rows) * len(windows)
    )
    submitted = [row for row in sessions if row.status == "submitted"]
    percentages = {row.id: _score_percentage(db, row) for row in sessions}
    passed = (
        None
        if paper.passing_percentage is None
        else sum(
            (percentages[row.id] or -1) >= float(paper.passing_percentage) for row in submitted
        )
    )
    failed = None if passed is None else len(submitted) - passed
    scores = [float(row.score) for row in submitted if row.score is not None]
    kpis = ReportKpis(
        eligible=eligible,
        started=len(sessions),
        submitted=len(submitted),
        in_progress=sum(row.status == "in_progress" for row in sessions),
        expired=sum(row.status == "expired" for row in sessions),
        not_started=not_started_count(eligible, len(sessions)),
        passed=passed,
        failed=failed,
        pass_rate=None
        if passed is None or not submitted
        else round(passed / len(submitted) * 100, 2),
        average_score=round(sum(scores) / len(scores), 2) if scores else None,
    )
    organizations = _organization_rows(db, quota_rows, windows, sessions, percentages, paper)
    people = _people_page(db, sessions, percentages, paper, filters)
    return ReportDashboard(
        exam_paper_id=str(paper.id),
        passing_percentage=float(paper.passing_percentage)
        if paper.passing_percentage is not None
        else None,
        kpis=kpis,
        attendance=[
            ReportSeriesItem(label=label, value=value)
            for label, value in (
                ("เข้าสอบแล้ว", kpis.started),
                ("ส่งแล้ว", kpis.submitted),
                ("กำลังสอบ", kpis.in_progress),
                ("หมดเวลา", kpis.expired),
                ("ยังไม่เข้าสอบ", kpis.not_started or 0),
            )
        ],
        pass_fail=[]
        if passed is None
        else [
            ReportSeriesItem(label="ผ่าน", value=passed),
            ReportSeriesItem(label="ไม่ผ่าน", value=failed or 0),
        ],
        organizations=organizations,
        people=people,
        generated_at=utc_now().isoformat() + "Z",
    )


def _organization_rows(
    db: Session,
    quotas: list[ExamPaperOrgUnit],
    windows: list[ExamWindow],
    sessions: list[ExamSession],
    percentages: dict[UUID, float | None],
    paper: ExamPaper,
) -> list[OrganizationReportRow]:
    result = []
    for quota in quotas:
        unit = db.get(OrgUnit, quota.org_unit_id)
        scoped = [row for row in sessions if row.eligibility_org_unit_id == quota.org_unit_id]
        submitted = [row for row in scoped if row.status == "submitted"]
        eligible = None if quota.eligible_count is None else quota.eligible_count * len(windows)
        passed = (
            None
            if paper.passing_percentage is None
            else sum(
                (percentages[row.id] or -1) >= float(paper.passing_percentage) for row in submitted
            )
        )
        scores = [float(row.score) for row in submitted if row.score is not None]
        result.append(
            OrganizationReportRow(
                org_unit_id=str(quota.org_unit_id),
                org_unit_name=unit.name if unit else "Unknown",
                eligible=eligible,
                started=len(scoped),
                submitted=len(submitted),
                passed=passed,
                failed=None if passed is None else len(submitted) - passed,
                attendance_rate=None if not eligible else round(len(scoped) / eligible * 100, 2),
                average_score=round(sum(scores) / len(scores), 2) if scores else None,
            )
        )
    return sorted(result, key=lambda row: row.org_unit_name)


def _people_page(
    db: Session,
    sessions: list[ExamSession],
    percentages: dict[UUID, float | None],
    paper: ExamPaper,
    filters: ReportFilters,
) -> PaginatedPeople:
    rows = []
    for session in sorted(sessions, key=lambda row: row.started_at, reverse=True):
        person = db.get(Person, session.person_id)
        unit = db.get(OrgUnit, session.org_unit_id)
        percentage = percentages[session.id]
        rows.append(
            PersonReportRow(
                session_id=str(session.id),
                person_id=str(session.person_id),
                full_name=person.full_name if person else "Unknown",
                org_unit_id=str(session.org_unit_id),
                org_unit_name=unit.name if unit else "Unknown",
                status=session.status,
                score=float(session.score) if session.score is not None else None,
                score_percentage=percentage,
                passed=pass_outcome(percentage, paper.passing_percentage),
                started_at=session.started_at.isoformat(),
                submitted_at=session.submitted_at.isoformat() if session.submitted_at else None,
            )
        )
    start = (filters.page - 1) * filters.page_size
    return PaginatedPeople(
        items=rows[start : start + filters.page_size],
        page=filters.page,
        page_size=filters.page_size,
        total=len(rows),
    )


def _empty_dashboard(filters: ReportFilters) -> ReportDashboard:
    return ReportDashboard(
        exam_paper_id=None,
        passing_percentage=None,
        kpis=ReportKpis(
            eligible=None,
            started=0,
            submitted=0,
            in_progress=0,
            expired=0,
            not_started=None,
            passed=None,
            failed=None,
            pass_rate=None,
            average_score=None,
        ),
        attendance=[],
        pass_fail=[],
        organizations=[],
        people=PaginatedPeople(items=[], page=filters.page, page_size=filters.page_size, total=0),
        generated_at=utc_now().isoformat() + "Z",
    )


def person_detail(db: Session, account: UserAccount, session_id: UUID) -> PersonReportDetail:
    session = db.get(ExamSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Exam session not found")
    variant = db.get(ExamVariant, session.exam_variant_id)
    paper = db.get(ExamPaper, variant.exam_paper_id) if variant else None
    if paper is None or paper.id not in {row.id for row in _visible_papers(db, account)}:
        raise HTTPException(status_code=403, detail="Exam session is outside report scope")
    if account.role == UserRole.EXAMINEE and session.person_id != account.person_id:
        raise HTTPException(status_code=403, detail="Examinees can only view their own results")
    percentage = _score_percentage(db, session)
    person = db.get(Person, session.person_id)
    unit = db.get(OrgUnit, session.org_unit_id)
    session_row = PersonReportRow(
        session_id=str(session.id),
        person_id=str(session.person_id),
        full_name=person.full_name if person else "Unknown",
        org_unit_id=str(session.org_unit_id),
        org_unit_name=unit.name if unit else "Unknown",
        status=session.status,
        score=float(session.score) if session.score is not None else None,
        score_percentage=percentage,
        passed=pass_outcome(percentage, paper.passing_percentage),
        started_at=session.started_at.isoformat(),
        submitted_at=session.submitted_at.isoformat() if session.submitted_at else None,
    )
    answers = {
        row.exam_variant_question_id: row
        for row in db.scalars(select(ExamAnswer).where(ExamAnswer.exam_session_id == session.id))
    }
    questions = []
    variant_questions = db.scalars(
        select(ExamVariantQuestion)
        .where(ExamVariantQuestion.exam_variant_id == session.exam_variant_id)
        .order_by(ExamVariantQuestion.order_index)
    )
    for row in variant_questions:
        version = db.get(QuestionVersion, row.question_version_id)
        choices = json.loads(version.choices_snapshot_text) if version else []
        selected_id = str(answers[row.id].selected_choice_id) if row.id in answers else None
        selected = next((choice for choice in choices if choice["id"] == selected_id), None)
        correct = next((choice for choice in choices if choice.get("is_correct")), None)
        reveal = session.status == "submitted"
        questions.append(
            ReportQuestionDetail(
                question_id=str(row.id),
                content=version.content_snapshot if version else "",
                selected_choice_id=selected_id,
                selected_choice=selected.get("content") if selected else None,
                correct_choice_id=correct.get("id") if correct and reveal else None,
                correct_choice=correct.get("content") if correct and reveal else None,
                is_correct=answers[row.id].is_correct_cache
                if row.id in answers and reveal
                else None,
                explanation=version.explanation if version and reveal else None,
            )
        )
    return PersonReportDetail(session=session_row, questions=questions)


def own_results(db: Session, account: UserAccount) -> list[PersonReportRow]:
    sessions = list(
        db.scalars(
            select(ExamSession)
            .where(ExamSession.person_id == account.person_id)
            .order_by(ExamSession.started_at.desc())
        )
    )
    result = []
    for session in sessions:
        variant = db.get(ExamVariant, session.exam_variant_id)
        paper = db.get(ExamPaper, variant.exam_paper_id) if variant else None
        if paper is None:
            continue
        result.extend(
            _people_page(
                db,
                [session],
                {session.id: _score_percentage(db, session)},
                paper,
                ReportFilters(page_size=1),
            ).items
        )
    return result


def question_analytics(db: Session, account: UserAccount, paper_id: UUID) -> QuestionAnalytics:
    paper = _selected_paper(db, account, ReportFilters(exam_paper_id=paper_id))
    if paper is None:
        raise HTTPException(status_code=404, detail="Exam Creation not found")
    variants = list(db.scalars(select(ExamVariant).where(ExamVariant.exam_paper_id == paper.id)))
    rows: list[QuestionAnalyticsRow] = []
    seen_versions: set[UUID] = set()
    for variant in variants:
        for question in db.scalars(
            select(ExamVariantQuestion).where(ExamVariantQuestion.exam_variant_id == variant.id)
        ):
            if question.question_version_id in seen_versions:
                continue
            seen_versions.add(question.question_version_id)
            version = db.get(QuestionVersion, question.question_version_id)
            equivalent_ids = list(
                db.scalars(
                    select(ExamVariantQuestion.id).where(
                        ExamVariantQuestion.question_version_id == question.question_version_id
                    )
                )
            )
            answers = list(
                db.scalars(
                    select(ExamAnswer).where(
                        ExamAnswer.exam_variant_question_id.in_(equivalent_ids)
                    )
                )
            )
            distribution: dict[str, int] = {}
            for answer in answers:
                key = str(answer.selected_choice_id)
                distribution[key] = distribution.get(key, 0) + 1
            correct = sum(answer.is_correct_cache is True for answer in answers)
            rows.append(
                QuestionAnalyticsRow(
                    question_id=str(question.question_version_id),
                    content=version.content_snapshot if version else "",
                    answer_total=len(answers),
                    correct_total=correct,
                    correct_rate=round(correct / len(answers) * 100, 2) if answers else None,
                    choice_distribution=distribution,
                )
            )
    variant_series = []
    for variant in variants:
        scores = [
            float(value)
            for value in db.scalars(
                select(ExamSession.score).where(
                    ExamSession.exam_variant_id == variant.id,
                    ExamSession.status == "submitted",
                    ExamSession.score.is_not(None),
                )
            )
        ]
        variant_series.append(
            ReportSeriesItem(
                label=variant.variant_label,
                value=round(sum(scores) / len(scores), 2) if scores else 0,
            )
        )
    return QuestionAnalytics(exam_paper_id=str(paper.id), questions=rows, variants=variant_series)
