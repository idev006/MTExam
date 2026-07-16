export interface ReportOption { id: string; label: string; parent_id: string | null }
export interface ReportContext {
  subjects: ReportOption[]; exam_creations: ReportOption[]; exam_windows: ReportOption[];
  organizations: ReportOption[]; default_exam_paper_id: string | null; role: string;
}
export interface ReportFilters {
  subject_id: string; exam_paper_id: string; exam_window_id: string;
  date_from: string; date_to: string; org_unit_id: string; page: number; page_size: number;
}
export interface ReportKpis {
  eligible: number | null; started: number; submitted: number; in_progress: number;
  expired: number; not_started: number | null; passed: number | null; failed: number | null;
  pass_rate: number | null; average_score: number | null;
}
export interface ReportSeriesItem { label: string; value: number }
export interface OrganizationReportRow {
  org_unit_id: string; org_unit_name: string; eligible: number | null; started: number;
  submitted: number; passed: number | null; failed: number | null;
  attendance_rate: number | null; average_score: number | null;
}
export interface PersonReportRow {
  session_id: string; person_id: string; full_name: string; org_unit_id: string;
  org_unit_name: string; status: string; score: number | null; score_percentage: number | null;
  passed: boolean | null; started_at: string; submitted_at: string | null;
}
export interface ReportDashboard {
  exam_paper_id: string | null; passing_percentage: number | null; kpis: ReportKpis;
  attendance: ReportSeriesItem[]; pass_fail: ReportSeriesItem[];
  organizations: OrganizationReportRow[];
  people: { items: PersonReportRow[]; page: number; page_size: number; total: number };
  generated_at: string;
}
export interface PersonReportDetail {
  session: PersonReportRow;
  questions: { question_id: string; content: string; selected_choice: string | null;
    correct_choice: string | null; is_correct: boolean | null; explanation: string | null }[];
}
export interface QuestionAnalytics {
  exam_paper_id: string;
  questions: { question_id: string; content: string; answer_total: number; correct_total: number;
    correct_rate: number | null; choice_distribution: Record<string, number> }[];
  variants: ReportSeriesItem[];
}
