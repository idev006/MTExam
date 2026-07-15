<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet } from "@/api/client";

interface Report { employee_total: number; employee_active: number; employee_inactive: number; exam_in_progress: number; exam_submitted: number; average_score: number | null; }
const report = ref<Report | null>(null); const error = ref(""); const loading = ref(true);
onMounted(async () => { try { report.value = await apiGet<Report>("/reports/summary"); } catch (e) { error.value = e instanceof Error ? e.message : "โหลดรายงานไม่สำเร็จ"; } finally { loading.value = false; } });
</script>
<template><PageContainer><PageHeader eyebrow="รายงาน" title="ภาพรวมระบบ" description="ข้อมูลสรุปแบบอ่านอย่างเดียวตามสิทธิ์ของผู้ใช้" /><AppAlert v-if="loading"><span class="loading loading-spinner loading-sm"></span>กำลังโหลดรายงาน</AppAlert><AppAlert v-else-if="error" type="error">{{ error }}</AppAlert><div v-else-if="report" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><div v-for="item in [{label:'บุคลากรทั้งหมด',value:report.employee_total},{label:'กำลังปฏิบัติงาน',value:report.employee_active},{label:'ไม่ปฏิบัติงาน',value:report.employee_inactive},{label:'กำลังทำข้อสอบ',value:report.exam_in_progress},{label:'ส่งข้อสอบแล้ว',value:report.exam_submitted},{label:'คะแนนเฉลี่ย',value:report.average_score ?? '-'}]" :key="item.label" class="stat rounded-2xl border border-base-300 bg-base-100 shadow-sm"><div class="stat-title">{{ item.label }}</div><div class="stat-value text-primary">{{ item.value }}</div></div></div></PageContainer></template>
