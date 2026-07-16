import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PaperLifecycleActions from "./PaperLifecycleActions.vue";

describe("PaperLifecycleActions", () => {
  it("opens a draft paper", async () => {
    const wrapper = mount(PaperLifecycleActions, { props: { status: "draft" } });
    await wrapper.get('[data-testid="publish-paper"]').trigger("click");
    expect(wrapper.emitted("request")).toEqual([["published"]]);
    expect(wrapper.find('[data-testid="draft-paper"]').exists()).toBe(false);
  });

  it("closes a published paper or requests returning it to draft", async () => {
    const wrapper = mount(PaperLifecycleActions, { props: { status: "published" } });
    await wrapper.get('[data-testid="archive-paper"]').trigger("click");
    await wrapper.get('[data-testid="draft-paper"]').trigger("click");
    expect(wrapper.emitted("request")).toEqual([["archived"], ["draft"]]);
  });

  it("reopens an archived paper", async () => {
    const wrapper = mount(PaperLifecycleActions, { props: { status: "archived" } });
    await wrapper.get('[data-testid="publish-paper"]').trigger("click");
    expect(wrapper.emitted("request")).toEqual([["published"]]);
  });
});
