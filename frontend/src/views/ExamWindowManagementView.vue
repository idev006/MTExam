<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { apiGet, apiRequest } from "@/api/client";
import AppAlert from "@/components/feedback/AppAlert.vue";
import ConfirmModal from "@/components/feedback/ConfirmModal.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import WindowLifecycleActions, { type WindowStatus } from "@/components/windows/WindowLifecycleActions.vue";

interface Paper { id: string; title: string; status: string; default_duration_minutes: number }
interface QuotaItem { org_unit_id: string; org_unit_name?: string; eligible_count: number; selected?: boolean }
interface QuotaPolicy { paper_id: string; default_duration_minutes: number; eligible_org_units: QuotaItem[] }
interface ExamWindow {
  id: string; exam_paper_id: string; paper_title: string; title: string; status: WindowStatus;
  duration_minutes: number; completion_policy: "fixed_end" | "full_duration";
  late_entry_minutes: number; window_open_at: string | null; window_close_at: string | null;
  eligible_org_units: QuotaItem[]; session_counts: Record<string, number>;
}

const papers = ref<Paper[]>([]);
const windows = ref<ExamWindow[]>([]);
const quotas = ref<QuotaItem[]>([]);
const loading = ref(true);
const busy = ref(false);
const message = ref("");
const error = ref("");
const pending = ref<{ window: ExamWindow; status: Exclude<WindowStatus, "scheduled"> } | null>(null);
const statusReason = ref("");
const form = reactive({
  exam_paper_id: "", title: "", duration_minutes: 60, completion_policy: "fixed_end",
  late_entry_minutes: 0, window_open_at: "", window_close_at: "",
});

const publishedPapers = computed(() => papers.value.filter((paper) => paper.status === "published"));
const canCreate = computed(() => Boolean(
  form.exam_paper_id && form.title.trim() && form.duration_minutes >= 1 && form.duration_minutes <= 600
  && form.window_open_at && form.window_close_at
  && new Date(form.window_close_at) > new Date(form.window_open_at)
  && quotas.value.some((quota) => quota.selected && quota.eligible_count >= 0),
));
const statusLabels: Record<WindowStatus, string> = {
  scheduled: "รอเปิด", open: "เปิดสอบ", suspended: "ระงับชั่วคราว", closed: "ปิดแล้ว", cancelled: "ยกเลิก",
};
const statusClasses: Record<WindowStatus, string> = {
  scheduled: "badge-info", open: "badge-success", suspended: "badge-warning", closed: "badge-ghost", cancelled: "badge-error",
};
const confirmText = computed(() => {
  if (!pending.value) return { title: "", message: "", label: "ยืนยัน" };
  const labels = { open: "เปิดรอบสอบ", suspended: "ระงับรอบสอบ", closed: "ปิดรอบสอบ", cancelled: "ยกเลิกรอบสอบ" };
  return {
    title: labels[pending.value.status],
    message: `ยืนยัน${labels[pending.value.status]} “${pending.value.window.title}” การปิดหรือระงับจะหยุดเฉพาะการเริ่ม session ใหม่`,
    label: labels[pending.value.status],
  };
});

async function load() {
  loading.value = true;
  try {
    [papers.value, windows.value] = await Promise.all([apiGet<Paper[]>("/papers"), apiGet<ExamWindow[]>("/exam-windows")]);
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "โหลดข้อมูลรอบสอบไม่สำเร็จ"; }
  finally { loading.value = false; }
}

async function loadPolicy() {
  quotas.value = [];
  if (!form.exam_paper_id) return;
  try {
    const policy = await apiGet<QuotaPolicy>(`/papers/${form.exam_paper_id}/quota-policy`);
    form.duration_minutes = policy.default_duration_minutes;
    quotas.value = policy.eligible_org_units.map((item) => ({ ...item, selected: true }));
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "โหลด quota template ไม่สำเร็จ"; }
}

async function createWindow() {
  if (!canCreate.value) return;
  busy.value = true; error.value = ""; message.value = "";
  try {
    await apiRequest("/exam-windows", "POST", {
      ...form,
      window_open_at: new Date(form.window_open_at).toISOString(),
      window_close_at: new Date(form.window_close_at).toISOString(),
      eligible_org_units: quotas.value.filter((item) => item.selected).map(({ org_unit_id, eligible_count }) => ({ org_unit_id, eligible_count })),
    });
    message.value = "สร้างรอบสอบแล้ว ระบบบันทึก quota และนโยบายเวลาสำหรับรอบนี้แยกจาก ExamPaper";
    await load();
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "สร้างรอบสอบไม่สำเร็จ"; }
  finally { busy.value = false; }
}

function requestStatus(window: ExamWindow, status: Exclude<WindowStatus, "scheduled">) {
  statusReason.value = "";
  pending.value = { window, status };
}
async function confirmStatus() {
  if (!pending.value) return;
  busy.value = true; error.value = "";
  try {
    const current = pending.value;
    await apiRequest(`/exam-windows/${current.window.id}/status`, "PATCH", {
      status: current.status,
      reason: statusReason.value.trim() || "ดำเนินการตาม lifecycle ของรอบสอบ",
    });
    message.value = `เปลี่ยนสถานะ “${current.window.title}” เป็น ${statusLabels[current.status]} แล้ว`;
    pending.value = null;
    await load();
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "เปลี่ยนสถานะรอบสอบไม่สำเร็จ"; }
  finally { busy.value = false; }
}
function displayDate(value: string | null) { return value ? new Date(value).toLocaleString("th-TH") : "ไม่กำหนด"; }

watch(() => form.exam_paper_id, loadPolicy);
onMounted(load);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Exam Operations" title="จัดรอบสอบ" description="เลือก ExamPaper ที่เปิดใช้งาน แล้วกำหนดเวลา นโยบายสิ้นสุด และ quota จริงของแต่ละรอบ" />
    <AppAlert v-if="message" type="success">{{ message }}</AppAlert>
    <AppAlert v-if="error" type="error">{{ error }}</AppAlert>

    <section class="card mb-6 border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
      <h2 class="card-title">สร้าง Exam Window</h2>
      <p class="text-sm text-base-content/60">ExamPaper เป็นแม่แบบข้อสอบ ส่วนข้อมูลในส่วนนี้คือรอบสอบจริงและสามารถกำหนด quota ต่างกันในแต่ละรอบ</p>
      <form class="grid min-w-0 grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4" @submit.prevent="createWindow">
        <label class="form-control min-w-0 xl:col-span-2"><span class="label-text">ExamPaper ที่เปิดใช้งาน</span><select v-model="form.exam_paper_id" class="select select-bordered w-full min-w-0" required><option disabled value="">เลือก ExamPaper</option><option v-for="paper in publishedPapers" :key="paper.id" :value="paper.id">{{ paper.title }}</option></select></label>
        <label class="form-control min-w-0 xl:col-span-2"><span class="label-text">ชื่อรอบสอบ</span><input v-model="form.title" class="input input-bordered w-full min-w-0" placeholder="เช่น รอบ บก.อก.ภ.6 เดือนกรกฎาคม" required /></label>
        <label class="form-control min-w-0"><span class="label-text">เปิดให้เริ่มสอบ</span><input v-model="form.window_open_at" class="input input-bordered w-full min-w-0" type="datetime-local" required /></label>
        <label class="form-control min-w-0"><span class="label-text">เวลาสุดท้ายที่เริ่มสอบ</span><input v-model="form.window_close_at" class="input input-bordered w-full min-w-0" type="datetime-local" required /></label>
        <label class="form-control min-w-0"><span class="label-text">ระยะเวลาทำข้อสอบ</span><div class="join w-full min-w-0"><input v-model.number="form.duration_minutes" class="input input-bordered join-item w-full min-w-0" type="number" min="1" max="600" required /><span class="btn join-item pointer-events-none">นาที</span></div></label>
        <label class="form-control min-w-0"><span class="label-text">นโยบายสิ้นสุด</span><select v-model="form.completion_policy" class="select select-bordered w-full min-w-0"><option value="fixed_end">หยุดพร้อมกันเมื่อปิดรอบ</option><option value="full_duration">ผู้เริ่มแล้วได้เวลาครบ</option></select></label>
        <label class="form-control min-w-0"><span class="label-text">อนุญาตเข้าสาย</span><div class="join w-full min-w-0"><input v-model.number="form.late_entry_minutes" class="input input-bordered join-item w-full min-w-0" type="number" min="0" max="1440" /><span class="btn join-item pointer-events-none">นาที</span></div></label>
        <div class="min-w-0 rounded-box border border-base-300 p-3 md:col-span-2 xl:col-span-4">
          <h3 class="font-semibold">Quota ของรอบสอบ</h3><p class="mb-3 text-xs text-base-content/60">คัดลอกจาก ExamPaper เป็นค่าเริ่มต้น การแก้ตรงนี้ไม่เปลี่ยนรอบอื่น</p>
          <div v-if="!quotas.length" class="text-sm text-base-content/50">เลือก ExamPaper เพื่อโหลด quota template</div>
          <div v-else class="grid min-w-0 grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3"><label v-for="quota in quotas" :key="quota.org_unit_id" class="flex min-w-0 items-center gap-3 rounded-box bg-base-200 p-3"><input v-model="quota.selected" class="checkbox checkbox-primary" type="checkbox" /><span class="min-w-0 flex-1 truncate">{{ quota.org_unit_name }}</span><input v-model.number="quota.eligible_count" class="input input-bordered input-sm w-20 shrink-0 sm:w-24" type="number" min="0" :disabled="!quota.selected" aria-label="จำนวนผู้มีสิทธิ์" /></label></div>
        </div>
        <div class="flex justify-end md:col-span-2 xl:col-span-4"><button class="btn btn-primary" type="submit" :disabled="!canCreate || busy"><span v-if="busy" class="loading loading-spinner loading-sm"></span>สร้างรอบสอบ</button></div>
      </form>
    </div></section>

    <section><div class="mb-3 flex items-center justify-between"><h2 class="text-xl font-bold">รอบสอบทั้งหมด</h2><span class="badge badge-outline">{{ windows.length }} รอบ</span></div>
      <div v-if="loading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><div v-for="index in 3" :key="index" class="skeleton h-60"></div></div>
      <div v-else-if="!windows.length" class="alert">ยังไม่มีรอบสอบ</div>
      <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article v-for="window in windows" :key="window.id" class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body p-5">
          <div class="flex items-start justify-between gap-3"><div><h3 class="font-bold">{{ window.title }}</h3><p class="text-sm text-base-content/60">{{ window.paper_title }}</p></div><span class="badge shrink-0" :class="statusClasses[window.status]">{{ statusLabels[window.status] }}</span></div>
          <dl class="grid grid-cols-2 gap-3 text-sm"><div><dt class="text-base-content/50">เปิดเริ่มสอบ</dt><dd>{{ displayDate(window.window_open_at) }}</dd></div><div><dt class="text-base-content/50">ปิดรับการเริ่ม</dt><dd>{{ displayDate(window.window_close_at) }}</dd></div><div><dt class="text-base-content/50">เวลาทำข้อสอบ</dt><dd>{{ window.duration_minutes }} นาที</dd></div><div><dt class="text-base-content/50">นโยบายเวลา</dt><dd>{{ window.completion_policy === 'full_duration' ? 'ได้เวลาครบหลังเริ่ม' : 'หยุดพร้อมกัน' }}</dd></div><div><dt class="text-base-content/50">Quota</dt><dd>{{ window.eligible_org_units.reduce((sum, item) => sum + item.eligible_count, 0) }} คน / {{ window.eligible_org_units.length }} หน่วย</dd></div><div><dt class="text-base-content/50">Session</dt><dd>{{ window.session_counts.total ?? 0 }} คน</dd></div></dl>
          <WindowLifecycleActions :status="window.status" @request="requestStatus(window, $event)" />
        </div></article>
      </div>
    </section>
    <ConfirmModal
      :open="Boolean(pending)"
      :title="confirmText.title"
      :message="confirmText.message"
      :confirm-label="confirmText.label"
      cancel-label="ยกเลิก"
      :busy="busy"
      :confirm-disabled="Boolean(pending && ['suspended', 'cancelled'].includes(pending.status) && !statusReason.trim())"
      @confirm="confirmStatus"
      @cancel="pending = null"
    >
      <label v-if="pending && ['suspended', 'cancelled'].includes(pending.status)" class="form-control">
        <span class="label-text">เหตุผล <span class="text-error">*</span></span>
        <textarea v-model="statusReason" class="textarea textarea-bordered" maxlength="500" placeholder="ระบุเหตุผลเพื่อบันทึกใน Audit Log"></textarea>
      </label>
    </ConfirmModal>
  </PageContainer>
</template>
