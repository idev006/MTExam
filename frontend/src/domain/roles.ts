export const USER_ROLES = [
  "super_admin",
  "division_admin",
  "bureau_admin",
  "station_admin",
  "exam_author",
  "exam_coordinator",
  "examinee",
  "viewer",
] as const;

export const AUTHOR_ROLES = ["super_admin", "exam_author"] as const;
export const WINDOW_CREATE_ROLES = ["super_admin", "exam_coordinator"] as const;
export const WINDOW_PAGE_ROLES = [
  "super_admin",
  "exam_author",
  "exam_coordinator",
] as const;
export const REPORT_ROLES = USER_ROLES;

export function hasRole(role: string | undefined, allowed: readonly string[]): boolean {
  return Boolean(role && allowed.includes(role));
}
