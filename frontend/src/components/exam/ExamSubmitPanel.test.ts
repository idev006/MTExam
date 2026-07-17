import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ExamSubmitPanel from "./ExamSubmitPanel.vue";

describe("ExamSubmitPanel", () => {
  it("requires DaisyUI modal confirmation and reports unanswered questions", async () => {
    const wrapper = mount(ExamSubmitPanel, {
      props: { status: "in_progress", answered: 7, total: 10, remaining: 60 },
    });

    expect(wrapper.emitted("submit")).toBeUndefined();
    await wrapper.get('[data-testid="request-submit"]').trigger("click");
    expect(wrapper.text()).toContain("ยังไม่ได้ตอบ 3 ข้อ");
    await wrapper.get(".modal .btn-primary").trigger("click");
    expect(wrapper.emitted("submit")).toHaveLength(1);
  });

  it("does not offer submission after a terminal status", () => {
    const wrapper = mount(ExamSubmitPanel, {
      props: { status: "submitted", answered: 10, total: 10, remaining: 0 },
    });
    expect(wrapper.find('[data-testid="request-submit"]').exists()).toBe(false);
  });
});
