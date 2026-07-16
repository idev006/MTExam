from __future__ import annotations

from pydantic import BaseModel, Field


class ReportOption(BaseModel):
    id: str
    label: str
    parent_id: str | None = None


class ReportContext(BaseModel):
    subjects: list[ReportOption]
    exam_creations: list[ReportOption]
    exam_windows: list[ReportOption]
    organizations: list[ReportOption]
    default_exam_paper_id: str | None
    role: str


class ReportKpis(BaseModel):
    eligible: int | None
    started: int
    submitted: int
    in_progress: int
    expired: int
    not_started: int | None
    passed: int | None
    failed: int | None
    pass_rate: float | None
    average_score: float | None


class ReportSeriesItem(BaseModel):
    label: str
    value: float


class OrganizationReportRow(BaseModel):
    org_unit_id: str
    org_unit_name: str
    eligible: int | None
    started: int
    submitted: int
    passed: int | None
    failed: int | None
    attendance_rate: float | None
    average_score: float | None


class PersonReportRow(BaseModel):
    session_id: str
    person_id: str
    full_name: str
    org_unit_id: str
    org_unit_name: str
    status: str
    score: float | None
    score_percentage: float | None
    passed: bool | None
    started_at: str
    submitted_at: str | None


class PaginatedPeople(BaseModel):
    items: list[PersonReportRow]
    page: int
    page_size: int
    total: int


class ReportDashboard(BaseModel):
    exam_paper_id: str | None
    passing_percentage: float | None
    kpis: ReportKpis
    attendance: list[ReportSeriesItem]
    pass_fail: list[ReportSeriesItem]
    organizations: list[OrganizationReportRow]
    people: PaginatedPeople
    generated_at: str


class ReportQuestionDetail(BaseModel):
    question_id: str
    content: str
    selected_choice_id: str | None
    selected_choice: str | None
    correct_choice_id: str | None
    correct_choice: str | None
    is_correct: bool | None
    explanation: str | None


class PersonReportDetail(BaseModel):
    session: PersonReportRow
    questions: list[ReportQuestionDetail]


class QuestionAnalyticsRow(BaseModel):
    question_id: str
    content: str
    answer_total: int
    correct_total: int
    correct_rate: float | None
    choice_distribution: dict[str, int] = Field(default_factory=dict)


class QuestionAnalytics(BaseModel):
    exam_paper_id: str
    questions: list[QuestionAnalyticsRow]
    variants: list[ReportSeriesItem]
