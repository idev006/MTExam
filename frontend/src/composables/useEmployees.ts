import { computed, ref } from "vue";

import type { EmployeeSummary } from "@/types/employee";

const demoEmployees: EmployeeSummary[] = [
  { cid: "1-2345-67890-12-3", rank: "พ.ต.อ.", name: "สมชาย ใจดี", position: "ผู้กำกับการ", unit: "กก.1 บก.น.6", status: "active", updatedAt: "วันนี้ 09:42" },
  { cid: "3-4567-89012-34-5", rank: "ร.ต.อ.", name: "กมลวรรณ แสงทอง", position: "รองสารวัตร", unit: "กก.2 บก.น.6", status: "changed", updatedAt: "วันนี้ 09:15" },
  { cid: "5-6789-01234-56-7", rank: "ด.ต.", name: "วิทยา รักษ์ดี", position: "ผู้บังคับหมู่", unit: "กก.3 บก.น.6", status: "active", updatedAt: "เมื่อวาน 16:20" },
  { cid: "7-8901-23456-78-9", rank: "ส.ต.อ.", name: "ปรีชา มั่นคง", position: "ผู้บังคับหมู่", unit: "กก.1 บก.น.6", status: "inactive", updatedAt: "เมื่อวาน 14:08" },
];

export function useEmployees() {
  const employees = ref<EmployeeSummary[]>(demoEmployees);
  const search = ref("");
  const isLoading = ref(false);

  const filteredEmployees = computed(() => {
    const query = search.value.trim().toLowerCase();
    if (!query) return employees.value;
    return employees.value.filter((employee) =>
      [employee.name, employee.cid, employee.position, employee.unit].some((value) => value.toLowerCase().includes(query)),
    );
  });

  async function refresh() {
    isLoading.value = true;
    await new Promise((resolve) => setTimeout(resolve, 350));
    isLoading.value = false;
  }

  return { employees, search, isLoading, filteredEmployees, refresh };
}
