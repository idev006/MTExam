import type { ReportFilters } from "@/types/reporting";

export function reportQuery(filters: ReportFilters): string {
  const values: Record<string, string> = {
    subject_id: filters.subject_id, exam_paper_id: filters.exam_paper_id,
    exam_window_id: filters.exam_window_id, date_from: filters.date_from,
    date_to: filters.date_to, org_unit_id: filters.org_unit_id,
    page: String(filters.page), page_size: String(filters.page_size),
  };
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) if (value) query.set(key, value);
  return query.toString();
}
