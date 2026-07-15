<script setup lang="ts">
import type { EmployeeSummary } from "@/types/employee";

defineProps<{ employees: EmployeeSummary[]; loading?: boolean }>();

const statusLabel: Record<EmployeeSummary["status"], string> = {
  active: "ปกติ",
  changed: "มีการเปลี่ยนแปลง",
  inactive: "ไม่ใช้งาน",
};
</script>

<template>
  <div class="overflow-x-auto">
    <table class="table">
      <thead><tr><th>บุคลากร</th><th>ตำแหน่ง</th><th>หน่วยงาน</th><th>สถานะ</th><th>ปรับปรุงล่าสุด</th></tr></thead>
      <tbody>
        <tr v-if="loading"><td colspan="5"><span class="loading loading-dots loading-sm"></span> กำลังโหลดข้อมูล</td></tr>
        <tr v-else-if="employees.length === 0"><td colspan="5" class="py-8 text-center text-base-content/60">ไม่พบข้อมูล</td></tr>
        <tr v-for="employee in employees" v-else :key="employee.cid" class="hover">
          <td><div class="font-medium">{{ employee.name }}</div><div class="text-xs text-base-content/50">{{ employee.rank }} · {{ employee.cid }}</div></td>
          <td>{{ employee.position }}</td><td>{{ employee.unit }}</td>
          <td><span class="badge" :class="{ 'badge-success': employee.status === 'active', 'badge-warning': employee.status === 'changed', 'badge-error': employee.status === 'inactive' }">{{ statusLabel[employee.status] }}</span></td>
          <td class="text-sm text-base-content/60">{{ employee.updatedAt }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
