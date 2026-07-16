<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { apiDownload, apiGet } from "@/api/client";
import { reportQuery } from "@/api/reporting";
import ReportCharts from "@/components/reports/ReportCharts.vue";
import ReportFiltersForm from "@/components/reports/ReportFiltersForm.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import type { PersonReportDetail, QuestionAnalytics, ReportContext, ReportDashboard, ReportFilters } from "@/types/reporting";

const context = ref<ReportContext | null>(null);
const dashboard = ref<ReportDashboard | null>(null);
const analytics = ref<QuestionAnalytics | null>(null);
const detail = ref<PersonReportDetail | null>(null);
const loading = ref(true);
const detailLoading = ref(false);
const exporting = ref("");
const error = ref("");
const filterDrawerOpen = ref(false);
const filters = reactive<ReportFilters>({
  subject_id: "", exam_paper_id: "", exam_window_id: "", date_from: "", date_to: "",
  org_unit_id: "", page: 1, page_size: 25,
});
const availableWindows = computed(() => context.value?.exam_windows.filter((row) =>
  !filters.exam_paper_id || row.parent_id === filters.exam_paper_id,
) ?? []);
const isAuthor = computed(() => context.value?.role === "exam_author");
const isExaminee = computed(() => context.value?.role === "examinee");
const kpiCards = computed(() => dashboard.value ? [
  ["ผู้มีสิทธิ์", dashboard.value.kpis.eligible ?? "ไม่ระบุ"],
  ["เข้าสอบ", dashboard.value.kpis.started], ["ส่งแล้ว", dashboard.value.kpis.submitted],
  ["ผ่าน", dashboard.value.kpis.passed ?? "N/A"], ["ไม่ผ่าน", dashboard.value.kpis.failed ?? "N/A"],
  ["อัตราผ่าน", dashboard.value.kpis.pass_rate === null ? "N/A" : `${dashboard.value.kpis.pass_rate}%`],
  ["คะแนนเฉลี่ย", dashboard.value.kpis.average_score ?? "-"],
] : []);

async function initialize() {
  loading.value = true; error.value = "";
  try {
    context.value = await apiGet<ReportContext>("/reports/context");
    filters.exam_paper_id = context.value.default_exam_paper_id ?? "";
    await loadDashboard();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "โหลดรายงานไม่สำเร็จ";
  } finally { loading.value = false; }
}
async function loadDashboard() {
  error.value = "";
  try {
    dashboard.value = await apiGet<ReportDashboard>(`/reports/dashboard?${reportQuery(filters)}`);
    if (isAuthor.value && dashboard.value.exam_paper_id) {
      analytics.value = await apiGet<QuestionAnalytics>(`/reports/question-analytics?exam_paper_id=${dashboard.value.exam_paper_id}`);
    } else analytics.value = null;
    filterDrawerOpen.value = false;
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "โหลดรายงานไม่สำเร็จ"; }
}
async function applyFilters() { filters.page = 1; loading.value = true; await loadDashboard(); loading.value = false; }
async function resetFilters() {
  Object.assign(filters, { subject_id: "", exam_paper_id: context.value?.default_exam_paper_id ?? "", exam_window_id: "", date_from: "", date_to: "", org_unit_id: "", page: 1 });
  await applyFilters();
}
async function changePage(page: number) { filters.page = page; loading.value = true; await loadDashboard(); loading.value = false; }
async function openDetail(sessionId: string) {
  detailLoading.value = true; detail.value = null;
  try { detail.value = await apiGet<PersonReportDetail>(`/reports/people/${sessionId}`); }
  catch (cause) { error.value = cause instanceof Error ? cause.message : "โหลดรายละเอียดไม่สำเร็จ"; }
  finally { detailLoading.value = false; }
}
async function exportReport(format: "pdf" | "xlsx" | "csv") {
  exporting.value = format;
  try { await apiDownload(`/reports/export?format=${format}&${reportQuery(filters)}`); }
  catch (cause) { error.value = cause instanceof Error ? cause.message : "ส่งออกรายงานไม่สำเร็จ"; }
  finally { exporting.value = ""; }
}
onMounted(initialize);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Reporting" :title="isExaminee ? 'ผลสอบของฉัน' : isAuthor ? 'วิเคราะห์ Exam Creation' : 'รายงานการสอบตามขอบเขตหน่วยงาน'" description="ข้อมูลทุกส่วนตรวจสิทธิ์และ scope ที่ backend และใช้ตัวกรองเดียวกับไฟล์ส่งออก">
      <template #actions><button class="btn btn-outline lg:hidden" @click="filterDrawerOpen = true">ตัวกรอง</button></template>
    </PageHeader>
    <AppAlert v-if="error" type="error"><span>{{ error }}</span><button class="btn btn-sm" @click="initialize">ลองใหม่</button></AppAlert>

    <div class="grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <aside class="hidden lg:block"><div class="card sticky top-20 border border-base-300 bg-base-100"><div class="card-body"><h2 class="card-title">ตัวกรองรายงาน</h2><ReportFiltersForm :context="context" :filters="filters" :windows="availableWindows" @apply="applyFilters" @reset="resetFilters" /></div></div></aside>
      <main class="min-w-0 space-y-6">
        <div v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><div v-for="index in 8" :key="index" class="skeleton h-28"></div></div>
        <template v-else-if="dashboard">
          <section class="grid gap-3 grid-cols-2 md:grid-cols-4 xl:grid-cols-7"><div v-for="card in kpiCards" :key="card[0]" class="stat rounded-box border border-base-300 bg-base-100 p-4"><div class="stat-title text-xs">{{ card[0] }}</div><div class="stat-value text-2xl text-primary">{{ card[1] }}</div></div></section>
          <ReportCharts :attendance="dashboard.attendance" :pass-fail="dashboard.pass_fail" :organizations="dashboard.organizations" />

          <section v-if="analytics" class="card border border-base-300 bg-base-100"><div class="card-body"><h2 class="card-title">คุณภาพข้อสอบ</h2><div class="overflow-x-auto"><table class="table table-sm"><thead><tr><th>คำถาม</th><th>คำตอบ</th><th>ตอบถูก</th><th>อัตราถูก</th></tr></thead><tbody><tr v-for="row in analytics.questions" :key="row.question_id"><td class="max-w-md whitespace-normal">{{ row.content }}</td><td>{{ row.answer_total }}</td><td>{{ row.correct_total }}</td><td>{{ row.correct_rate ?? '-' }}%</td></tr><tr v-if="!analytics.questions.length"><td colspan="4" class="text-center">ยังไม่มีคำตอบสำหรับวิเคราะห์</td></tr></tbody></table></div></div></section>

          <section v-if="!isExaminee" class="card border border-base-300 bg-base-100"><div class="card-body"><h2 class="card-title">เปรียบเทียบรายหน่วยงาน</h2><div class="hidden overflow-x-auto sm:block"><table class="table"><thead><tr><th>หน่วยงาน</th><th>ผู้มีสิทธิ์</th><th>เข้าสอบ</th><th>ส่งแล้ว</th><th>ผ่าน/ไม่ผ่าน</th><th>Attendance</th><th>คะแนนเฉลี่ย</th></tr></thead><tbody><tr v-for="row in dashboard.organizations" :key="row.org_unit_id"><td>{{ row.org_unit_name }}</td><td>{{ row.eligible ?? 'ไม่ระบุ' }}</td><td>{{ row.started }}</td><td>{{ row.submitted }}</td><td>{{ row.passed ?? '-' }} / {{ row.failed ?? '-' }}</td><td>{{ row.attendance_rate ?? '-' }}%</td><td>{{ row.average_score ?? '-' }}</td></tr></tbody></table></div><div class="grid gap-3 sm:hidden"><article v-for="row in dashboard.organizations" :key="row.org_unit_id" class="rounded-box border border-base-300 p-3"><h3 class="font-bold">{{ row.org_unit_name }}</h3><p>เข้าสอบ {{ row.started }} / {{ row.eligible ?? 'ไม่ระบุ' }}</p><progress class="progress progress-primary" :value="row.attendance_rate ?? 0" max="100"></progress><p class="text-sm">ผ่าน {{ row.passed ?? '-' }} · ไม่ผ่าน {{ row.failed ?? '-' }} · เฉลี่ย {{ row.average_score ?? '-' }}</p></article></div></div></section>

          <section class="card border border-base-300 bg-base-100"><div class="card-body"><div class="flex flex-wrap items-center justify-between gap-3"><h2 class="card-title">{{ isExaminee ? 'ประวัติการสอบ' : 'รายบุคคล' }}</h2><span class="badge badge-ghost">{{ dashboard.people.total }} รายการ</span></div><div class="overflow-x-auto"><table class="table"><thead><tr><th>ชื่อ</th><th>หน่วยงาน</th><th>สถานะ</th><th>คะแนน</th><th>ผล</th><th></th></tr></thead><tbody><tr v-for="row in dashboard.people.items" :key="row.session_id"><td>{{ row.full_name }}</td><td>{{ row.org_unit_name }}</td><td><span class="badge badge-outline">{{ row.status }}</span></td><td>{{ row.score_percentage ?? '-' }}%</td><td><span v-if="row.passed !== null" class="badge" :class="row.passed ? 'badge-success' : 'badge-error'">{{ row.passed ? 'ผ่าน' : 'ไม่ผ่าน' }}</span><span v-else>-</span></td><td><button class="btn btn-ghost btn-sm" @click="openDetail(row.session_id)">รายละเอียด</button></td></tr><tr v-if="!dashboard.people.items.length"><td colspan="6" class="py-10 text-center text-base-content/60">ยังไม่มีข้อมูลตามตัวกรอง</td></tr></tbody></table></div><div class="join self-end"><button class="btn join-item" :disabled="filters.page <= 1" @click="changePage(filters.page - 1)">ก่อนหน้า</button><button class="btn join-item btn-disabled">หน้า {{ filters.page }}</button><button class="btn join-item" :disabled="filters.page * filters.page_size >= dashboard.people.total" @click="changePage(filters.page + 1)">ถัดไป</button></div></div></section>

          <section class="flex flex-wrap items-center justify-between gap-3 rounded-box border border-base-300 bg-base-100 p-4"><p class="text-sm text-base-content/60">อัปเดต {{ new Date(dashboard.generated_at).toLocaleString('th-TH') }}</p><div class="flex flex-wrap gap-2"><button v-for="format in ['pdf','xlsx','csv'] as const" :key="format" class="btn btn-outline btn-sm" :disabled="Boolean(exporting)" @click="exportReport(format)"><span v-if="exporting === format" class="loading loading-spinner loading-xs"></span>{{ format.toUpperCase() }}</button><button class="btn btn-ghost btn-sm" @click="resetFilters">รีเซ็ต</button></div></section>
        </template>
      </main>
    </div>

    <div v-if="filterDrawerOpen" class="fixed inset-0 z-50 bg-black/40 lg:hidden" @click.self="filterDrawerOpen = false"><aside class="ml-auto h-full w-[min(90vw,22rem)] overflow-y-auto bg-base-100 p-5 shadow-xl"><div class="mb-4 flex justify-between"><h2 class="text-lg font-bold">ตัวกรองรายงาน</h2><button class="btn btn-square btn-ghost btn-sm" @click="filterDrawerOpen = false">✕</button></div><ReportFiltersForm :context="context" :filters="filters" :windows="availableWindows" @apply="applyFilters" @reset="resetFilters" /></aside></div>
    <div v-if="detailLoading || detail" class="modal modal-open"><div class="modal-box max-w-4xl"><button class="btn btn-circle btn-ghost btn-sm absolute right-3 top-3" @click="detail = null">✕</button><span v-if="detailLoading" class="loading loading-spinner loading-lg"></span><template v-else-if="detail"><h2 class="text-xl font-bold">{{ detail.session.full_name }}</h2><p class="text-sm text-base-content/60">{{ detail.session.org_unit_name }} · {{ detail.session.score_percentage ?? '-' }}%</p><div class="mt-4 grid gap-3"><article v-for="(question, index) in detail.questions" :key="question.question_id" class="rounded-box border border-base-300 p-4"><h3 class="font-semibold">{{ index + 1 }}. {{ question.content }}</h3><p>ตอบ: {{ question.selected_choice ?? 'ไม่ได้ตอบ' }}</p><p v-if="question.correct_choice" class="text-success">คำตอบที่ถูก: {{ question.correct_choice }}</p><p v-if="question.explanation" class="mt-2 text-sm text-base-content/70">เหตุผล: {{ question.explanation }}</p></article></div></template></div><div class="modal-backdrop" @click="detail = null"></div></div>
  </PageContainer>
</template>
