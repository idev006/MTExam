import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import OrgQuotaTree from "@/components/papers/OrgQuotaTree.vue";
import { hasQuotaOverlap, sortOrgUnitsByName, type QuotaOrgUnit } from "@/components/papers/orgQuota";

const units: QuotaOrgUnit[] = [
  { id: "bureau", code: "B", name: "กองบังคับการอำนวยการ", level: "bureau", parent_id: null, status: "active" },
  { id: "division-1", code: "D1", name: "ฝ่ายอำนวยการ 1", level: "sub_unit", parent_id: "bureau", status: "active" },
  { id: "division-6", code: "D6", name: "ฝ่ายอำนวยการ 6", level: "sub_unit", parent_id: "bureau", status: "active" },
];

describe("OrgQuotaTree", () => {
  it("marks descendants as covered when their parent owns the shared quota", () => {
    const wrapper = mount(OrgQuotaTree, {
      props: { units, selectedIds: ["bureau"], quotaCounts: { bureau: 100 } },
    });

    expect(wrapper.get('[data-testid="org-select-division-6"]').attributes("disabled")).toBeDefined();
    expect(wrapper.text()).toContain("ครอบคลุมโดย “กองบังคับการอำนวยการ”");
    expect(wrapper.text()).toContain("โควต้าร่วม ครอบคลุม 2 หน่วยลูก");
  });

  it("blocks the ancestor but leaves sibling units selectable for child quotas", () => {
    const wrapper = mount(OrgQuotaTree, {
      props: { units, selectedIds: ["division-6"], quotaCounts: { "division-6": 500 } },
    });

    expect(wrapper.get('[data-testid="org-select-bureau"]').attributes("disabled")).toBeDefined();
    expect(wrapper.get('[data-testid="org-select-division-1"]').attributes("disabled")).toBeUndefined();
    expect(wrapper.text()).toContain("เลือกไม่ได้ เพราะมีการกำหนดโควต้าที่หน่วยลูกแล้ว");
  });

  it("emits selection and quota changes", async () => {
    const wrapper = mount(OrgQuotaTree, {
      props: { units, selectedIds: ["division-6"], quotaCounts: { "division-6": 500 } },
    });

    await wrapper.get('[data-testid="org-select-division-1"]').setValue(true);
    await wrapper.get('[data-testid="org-quota-division-6"]').setValue("450");

    expect(wrapper.emitted("toggle")?.[0]).toEqual(["division-1", true]);
    expect(wrapper.emitted("updateQuota")?.at(-1)).toEqual(["division-6", 450]);
  });
});

describe("hasQuotaOverlap", () => {
  it("detects a parent-child selection as a defensive submit guard", () => {
    expect(hasQuotaOverlap(units, ["bureau", "division-6"])).toBe(true);
    expect(hasQuotaOverlap(units, ["division-1", "division-6"])).toBe(false);
  });
});

describe("sortOrgUnitsByName", () => {
  it("sorts organization options alphabetically by display name", () => {
    expect(sortOrgUnitsByName([
      { id: "z", code: "Z", name: "Zulu", level: "bureau", parent_id: null, status: "active" },
      { id: "a", code: "A", name: "Alpha", level: "bureau", parent_id: null, status: "active" },
      { id: "b", code: "B", name: "Alpha", level: "station", parent_id: null, status: "active" },
    ]).map((unit) => unit.id)).toEqual(["a", "b", "z"]);
  });
});
