import { describe, expect, it } from "vitest";
import { reportQuery } from "@/api/reporting";

describe("reportQuery", () => {
  it("serializes one shared filter model and omits empty values", () => {
    const query = reportQuery({
      subject_id: "subject-1", exam_paper_id: "paper-1", exam_window_id: "",
      date_from: "2026-07-01", date_to: "", org_unit_id: "org-1", page: 2, page_size: 25,
    });
    const values = new URLSearchParams(query);
    expect(values.get("exam_paper_id")).toBe("paper-1");
    expect(values.get("org_unit_id")).toBe("org-1");
    expect(values.get("page")).toBe("2");
    expect(values.has("exam_window_id")).toBe(false);
  });
});
