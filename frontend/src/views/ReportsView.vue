<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet } from "@/api/client";

interface Report { employee_total: number; employee_active: number; employee_inactive: number; exam_in_progress: number; exam_submitted: number; average_score: number | null }
interface Creation { paper_id: string; title: string; variant_count: number; session_total: number; submitted_total: number; average_score: number | null }
interface Organization { org_unit_id: string; org_unit_name: string; session_total: number; submitted_total: number; average_score: number | null }
const report = ref<Report | null>(null); const creations = ref<Creation[]>([]); const organizations = ref<Organization[]>([]); const error = ref(""); const loading = ref(true);
onMounted(async () => { try { [report.value, creations.value, organizations.value] = await Promise.all([apiGet<Report>("/reports/summary"), apiGet<Creation[]>("/reports/exam-creations"), apiGet<Organization[]>("/reports/organizations")]); } catch (e) { error.value = e instanceof Error ? e.message : "โหลดรายงานไม่สำเร็จ"; } finally { loading.value = false; } });
</script>

<template>
  <PageContainer><PageHeader eyebrow="รายงาน" title="สถิติภาพรวมและแยกตามหน่วยงาน" description="ผู้บริหารเห็นภาพรวม ส่วนผู้ดูแลหน่วยเห็นหน่วยตนเองและหน่วยลูกตาม scope" />
    <AppAlert v-if="loading"><span class="loading loading-spinner loading-sm"></span>กำลังโหลดรายงาน</AppAlert><AppAlert v-else-if="error" type="error">{{ error }}</AppAlert>
    <template v-else><div v-if="report" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><div v-for="item in [{label:'บุคลากรทั้งหมด',value:report.employee_total},{label:'กำลังทำข้อสอบ',value:report.exam_in_progress},{label:'ส่งข้อสอบแล้ว',value:report.exam_submitted},{label:'คะแนนเฉลี่ย',value:report.average_score ?? '-'}]" :key="item.label" class="stat rounded-2xl border border-base-300 bg-base-100 shadow-sm"><div class="stat-title">{{ item.label }}</div><div class="stat-value text-primary">{{ item.value }}</div></div></div>
      <section class="mt-6 card border border-base-300 bg-base-100 shadow-sm"><div class="card-body overflow-x-auto"><h2 class="card-title">สถิติแยกตามหน่วยงาน</h2><table class="table"><thead><tr><th>หน่วยงาน</th><th>ผู้เข้าสอบ</th><th>ส่งแล้ว</th><th>คะแนนเฉลี่ย</th></tr></thead><tbody><tr v-for="item in organizations" :key="item.org_unit_id"><td>{{ item.org_unit_name }}</td><td>{{ item.session_total }}</td><td>{{ item.submitted_total }}</td><td>{{ item.average_score ?? '-' }}</td></tr><tr v-if="!organizations.length"><td colspan="4" class="text-center text-base-content/60">ยังไม่มีข้อมูล</td></tr></tbody></table></div></section>
      <section class="mt-6 card border border-base-300 bg-base-100 shadow-sm"><div class="card-body overflow-x-auto"><h2 class="card-title">สถิติราย Exam Creation</h2><table class="table"><thead><tr><th>ชุดข้อสอบ</th><th>Variants</th><th>ผู้เข้าสอบ</th><th>ส่งแล้ว</th><th>คะแนนเฉลี่ย</th></tr></thead><tbody><tr v-for="creation in creations" :key="creation.paper_id"><td>{{ creation.title }}</td><td>{{ creation.variant_count }}</td><td>{{ creation.session_total }}</td><td>{{ creation.submitted_total }}</td><td>{{ creation.average_score ?? '-' }}</td></tr></tbody></table></div></section>
    </template>
  </PageContainer>
</template>
