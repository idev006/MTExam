<script setup lang="ts">
import { computed } from "vue";
import { use } from "echarts/core";
import { BarChart, PieChart } from "echarts/charts";
import { AriaComponent, GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";
import type { OrganizationReportRow, ReportSeriesItem } from "@/types/reporting";

use([BarChart, PieChart, AriaComponent, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer]);
const props = defineProps<{
  attendance: ReportSeriesItem[];
  passFail: ReportSeriesItem[];
  organizations: OrganizationReportRow[];
}>();

const attendanceOption = computed(() => ({
  aria: { enabled: true, description: "กราฟสถานะการเข้าสอบ" },
  tooltip: { trigger: "item" }, legend: { bottom: 0 },
  series: [{ type: "pie", radius: ["42%", "70%"], data: props.attendance.map((row) => ({ name: row.label, value: row.value })) }],
}));
const passOption = computed(() => ({
  aria: { enabled: true, description: "กราฟผลผ่านและไม่ผ่าน" },
  tooltip: { trigger: "item" }, legend: { bottom: 0 },
  series: [{ type: "pie", radius: "70%", data: props.passFail.map((row) => ({ name: row.label, value: row.value })) }],
}));
const organizationOption = computed(() => ({
  aria: { enabled: true, description: "กราฟเปรียบเทียบอัตราเข้าสอบและคะแนนเฉลี่ยรายหน่วย" },
  tooltip: { trigger: "axis" }, legend: { top: 0 }, grid: { left: 45, right: 20, bottom: 70 },
  xAxis: { type: "category", data: props.organizations.map((row) => row.org_unit_name), axisLabel: { rotate: 25 } },
  yAxis: { type: "value", max: 100 },
  series: [
    { name: "เข้าสอบ (%)", type: "bar", data: props.organizations.map((row) => row.attendance_rate ?? 0) },
    { name: "คะแนนเฉลี่ย", type: "bar", data: props.organizations.map((row) => row.average_score ?? 0) },
  ],
}));
</script>

<template>
  <div class="grid min-w-0 gap-4 lg:grid-cols-12">
    <article class="card border border-base-300 bg-base-100 lg:col-span-4"><div class="card-body"><h2 class="card-title">การเข้าสอบ</h2><VChart v-if="attendance.length" class="h-72" :option="attendanceOption" autoresize /><p v-else class="py-16 text-center text-base-content/60">ยังไม่มีข้อมูล</p><details class="collapse collapse-arrow"><summary class="collapse-title text-sm">ดูข้อมูลกราฟเป็นตาราง</summary><div class="collapse-content"><table class="table table-sm"><tbody><tr v-for="row in attendance" :key="row.label"><th>{{ row.label }}</th><td>{{ row.value }}</td></tr></tbody></table></div></details></div></article>
    <article class="card border border-base-300 bg-base-100 lg:col-span-4"><div class="card-body"><h2 class="card-title">ผ่าน / ไม่ผ่าน</h2><VChart v-if="passFail.length" class="h-72" :option="passOption" autoresize /><p v-else class="py-16 text-center text-base-content/60">ยังไม่มีเกณฑ์ผ่านหรือผลสอบ</p><details class="collapse collapse-arrow"><summary class="collapse-title text-sm">ดูข้อมูลกราฟเป็นตาราง</summary><div class="collapse-content"><table class="table table-sm"><tbody><tr v-for="row in passFail" :key="row.label"><th>{{ row.label }}</th><td>{{ row.value }}</td></tr></tbody></table></div></details></div></article>
    <article class="card border border-base-300 bg-base-100 lg:col-span-4"><div class="card-body"><h2 class="card-title">เปรียบเทียบหน่วยงาน</h2><VChart v-if="organizations.length" class="h-72" :option="organizationOption" autoresize /><p v-else class="py-16 text-center text-base-content/60">ไม่มีข้อมูลหน่วยงานใน scope</p></div></article>
  </div>
</template>

<style scoped>
.echarts {
  width: 100%;
  min-width: 0;
  height: 18rem;
}
</style>
