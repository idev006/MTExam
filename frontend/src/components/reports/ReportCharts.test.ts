import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import ReportCharts from "@/components/reports/ReportCharts.vue";

vi.mock("vue-echarts", () => ({ default: { template: "<div data-chart></div>" } }));

describe("ReportCharts", () => {
  it("provides a table fallback for chart values", () => {
    const wrapper = mount(ReportCharts, {
      props: { attendance: [{ label: "ส่งแล้ว", value: 4 }], passFail: [], organizations: [] },
    });
    expect(wrapper.text()).toContain("ส่งแล้ว");
    expect(wrapper.text()).toContain("4");
    expect(wrapper.text()).toContain("ยังไม่มีเกณฑ์ผ่านหรือผลสอบ");
  });
});
