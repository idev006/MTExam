import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import PaperEditActions from "./PaperEditActions.vue";

describe("PaperEditActions", () => {
  it("offers direct edit only for an editable Draft", async () => {
    const wrapper = mount(PaperEditActions, { props: { canEdit: true, canRevise: true, revisionNumber: 1 } });
    await wrapper.get('[data-testid="edit-paper"]').trigger("click");
    expect(wrapper.emitted("edit")).toHaveLength(1);
  });

  it("offers a safe revision to an authorized owner", async () => {
    const wrapper = mount(PaperEditActions, { props: { canEdit: false, canRevise: true, revisionNumber: 2 } });
    expect(wrapper.find('[data-testid="edit-paper"]').exists()).toBe(false);
    expect(wrapper.text()).toContain("Revision 3");
    await wrapper.get('[data-testid="revise-paper"]').trigger("click");
    expect(wrapper.emitted("revise")).toHaveLength(1);
  });

  it("hides both mutation actions from a non-owner", () => {
    const wrapper = mount(PaperEditActions, { props: { canEdit: false, canRevise: false, revisionNumber: 1 } });
    expect(wrapper.find('[data-testid="edit-paper"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="revise-paper"]').exists()).toBe(false);
  });
});
