import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PageContainer from "@/components/layout/PageContainer.vue";

describe("PageContainer", () => {
  it("uses the full viewport width with responsive page gutters", () => {
    const wrapper = mount(PageContainer, {
      slots: { default: "Dashboard content" },
    });

    const container = wrapper.get("main");
    expect(container.classes()).toContain("w-full");
    expect(container.classes()).toContain("2xl:px-10");
    expect(container.attributes("class")).not.toMatch(/max-w-/);
    expect(container.text()).toBe("Dashboard content");
  });
});
