import { describe, expect, it } from "vitest";
import {
  AUTHOR_ROLES,
  REPORT_ROLES,
  WINDOW_CREATE_ROLES,
  WINDOW_PAGE_ROLES,
  hasRole,
} from "./roles";

describe("role capabilities", () => {
  it("separates content authoring from new Exam Window scheduling", () => {
    expect(hasRole("exam_author", AUTHOR_ROLES)).toBe(true);
    expect(hasRole("exam_author", WINDOW_CREATE_ROLES)).toBe(false);
    expect(hasRole("exam_coordinator", AUTHOR_ROLES)).toBe(false);
    expect(hasRole("exam_coordinator", WINDOW_CREATE_ROLES)).toBe(true);
  });

  it("keeps authors on the operation page for legacy windows", () => {
    expect(hasRole("exam_author", WINDOW_PAGE_ROLES)).toBe(true);
    expect(hasRole("exam_coordinator", WINDOW_PAGE_ROLES)).toBe(true);
  });

  it("includes the coordinator in scoped reporting", () => {
    expect(hasRole("exam_coordinator", REPORT_ROLES)).toBe(true);
    expect(hasRole(undefined, REPORT_ROLES)).toBe(false);
  });
});
