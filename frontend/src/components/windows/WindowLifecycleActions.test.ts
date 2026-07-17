import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import WindowLifecycleActions from "./WindowLifecycleActions.vue";

describe("WindowLifecycleActions", () => {
  it("offers open and cancel for a scheduled window", async () => {
    const wrapper = mount(WindowLifecycleActions, { props: { status: "scheduled" } });
    await wrapper.get('[data-testid="open-window"]').trigger("click");
    await wrapper.get('[data-testid="cancel-window"]').trigger("click");
    expect(wrapper.emitted("request")).toEqual([["open"], ["cancelled"]]);
  });

  it("offers suspend and close while open", async () => {
    const wrapper = mount(WindowLifecycleActions, { props: { status: "open" } });
    await wrapper.get('[data-testid="suspend-window"]').trigger("click");
    await wrapper.get('[data-testid="close-window"]').trigger("click");
    expect(wrapper.emitted("request")).toEqual([["suspended"], ["closed"]]);
  });

  it("does not expose mutations for terminal states", () => {
    const wrapper = mount(WindowLifecycleActions, { props: { status: "closed" } });
    expect(wrapper.find("button").exists()).toBe(false);
    expect(wrapper.text()).toContain("รอบสอบสิ้นสุดแล้ว");
  });
});
