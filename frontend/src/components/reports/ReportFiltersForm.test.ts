import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ReportFiltersForm from "@/components/reports/ReportFiltersForm.vue";

describe("ReportFiltersForm", () => {
  it("renders only scoped options and hides organization for examinees", () => {
    const filters = { subject_id: "", exam_paper_id: "", exam_window_id: "", date_from: "", date_to: "", org_unit_id: "", page: 1, page_size: 25 };
    const wrapper = mount(ReportFiltersForm, {
      props: {
        filters, windows: [],
        context: { role: "examinee", default_exam_paper_id: null, subjects: [], exam_creations: [], exam_windows: [], organizations: [{ id: "hidden", label: "Secret", parent_id: null }] },
      },
    });
    expect(wrapper.text()).not.toContain("Secret");
    expect(wrapper.find("form").exists()).toBe(true);
  });
});
