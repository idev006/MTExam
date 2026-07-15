export type EmployeeStatus = "active" | "inactive" | "changed";

export interface EmployeeSummary {
  cid: string;
  rank: string;
  name: string;
  position: string;
  unit: string;
  status: EmployeeStatus;
  updatedAt: string;
}
