<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import ConfirmModal from "@/components/feedback/ConfirmModal.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import OrgQuotaTree from "@/components/papers/OrgQuotaTree.vue";
import PaperEditActions from "@/components/papers/PaperEditActions.vue";
import PaperLifecycleActions, { type PaperLifecycleStatus } from "@/components/papers/PaperLifecycleActions.vue";
import { hasQuotaOverlap, type QuotaOrgUnit } from "@/components/papers/orgQuota";
import { apiGet, apiRequest } from "@/api/client";

interface Subject { id: string; code: string; name: string }
interface Question { id: string; content: string; difficulty: string | null; bank_name: string }
interface Paper {
  id: string; title: string; status: PaperLifecycleStatus; question_count: number;
  desired_question_count: number; default_duration_minutes: number;
  allowed_org_unit_count: number; passing_percentage: number | null;
  revision_number: number; based_on_paper_id: string | null; change_summary: string | null;
  window_count: number; session_count: number; can_edit: boolean; can_revise: boolean;
}
interface PaperEdit {
  id: string; title: string; org_unit_id: string; subject_id: string | null; question_ids: string[];
  desired_question_count: number; default_duration_minutes: number;
  eligible_org_units: Array<{ org_unit_id: string; eligible_count: number }>;
  passing_percentage: number; variant_count: number; question_selection_mode: string;
  pool_criteria: Record<string, unknown> | null; change_summary: string | null;
}

const subjects = ref<Subject[]>([]);
const orgUnits = ref<QuotaOrgUnit[]>([]);
const questions = ref<Question[]>([]);
const papers = ref<Paper[]>([]);
const selectedIds = ref<string[]>([]);
const selectedOrgIds = ref<string[]>([]);
const quotaCounts = reactive<Record<string, number>>({});
const search = ref("");
const message = ref("");
const error = ref("");
const loading = ref(false);
const papersLoading = ref(false);
const statusBusy = ref(false);
const pendingStatus = ref<{ paper: Paper; status: PaperLifecycleStatus } | null>(null);
const editingId = ref<string | null>(null);
const preserveQuestionSelection = ref(false);
const revisionPending = ref<Paper | null>(null);
const revisionTitle = ref("");
const revisionSummary = ref("");
const form = reactive({
  title: "", org_unit_id: "", subject_id: "", desired_question_count: 10,
  variant_count: 1, passing_percentage: 60, default_duration_minutes: 60,
  question_selection_mode: "fixed_set", pool_criteria: null as Record<string, unknown> | null,
  change_summary: "",
});

const statusLabels: Record<PaperLifecycleStatus, string> = {
  draft: "ร่าง", published: "เปิดใช้งาน", archived: "ปิดใช้งาน",
};
const statusClasses: Record<PaperLifecycleStatus, string> = {
  draft: "badge-ghost", published: "badge-success", archived: "badge-warning",
};
const confirmation = computed(() => {
  if (!pendingStatus.value) return { title: "", message: "", label: "ยืนยัน" };
  const { paper, status } = pendingStatus.value;
  if (status === "published") return {
    title: "เปิดใช้งาน Exam Creation",
    message: `ยืนยันเปิดใช้งาน “${paper.title}” เพื่อให้สร้าง Exam Window ได้`,
    label: "เปิดใช้งาน",
  };
  if (status === "archived") return {
    title: "ปิดใช้งาน Exam Creation",
    message: `ยืนยันปิดใช้งาน “${paper.title}” การสอบที่เริ่มแล้วจะไม่ถูกยกเลิก`,
    label: "ปิดใช้งาน",
  };
  return {
    title: "กลับเป็น Draft",
    message: `ยืนยันนำ “${paper.title}” กลับเป็น Draft ทำได้เฉพาะเมื่อยังไม่เคยสร้าง Exam Window`,
    label: "กลับเป็น Draft",
  };
});

const filteredQuestions = computed(() => questions.value.filter((question) =>
  !search.value || `${question.content} ${question.bank_name}`.toLowerCase().includes(search.value.toLowerCase()),
));
const canSubmit = computed(() => Boolean(
  form.title && form.subject_id && form.org_unit_id && selectedOrgIds.value.length
  && selectedIds.value.length >= form.desired_question_count
  && form.passing_percentage >= 0 && form.passing_percentage <= 100
  && Number.isInteger(form.default_duration_minutes)
  && form.default_duration_minutes >= 1 && form.default_duration_minutes <= 600
  && !hasQuotaOverlap(orgUnits.value, selectedOrgIds.value)
  && selectedOrgIds.value.every((id) => Number.isInteger(quotaCounts[id]) && quotaCounts[id] >= 0)
  && (!editingId.value || form.change_summary.trim().length >= 3),
));

async function loadBase() {
  papersLoading.value = true;
  try {
    [subjects.value, orgUnits.value, papers.value] = await Promise.all([
      apiGet<Subject[]>("/question-banks/subjects"), apiGet<QuotaOrgUnit[]>("/org-units"),
      apiGet<Paper[]>("/papers"),
    ]);
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "โหลดข้อมูลไม่สำเร็จ";
  } finally { papersLoading.value = false; }
}
async function loadQuestions() {
  if (!form.subject_id) { questions.value = []; return; }
  loading.value = true;
  try {
    questions.value = await apiGet<Question[]>(`/question-banks/questions?subject_id=${form.subject_id}`);
    if (!preserveQuestionSelection.value) selectedIds.value = [];
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "โหลดคำถามไม่สำเร็จ";
  } finally { loading.value = false; }
}
function toggleOrganization(id: string, checked: boolean) {
  selectedOrgIds.value = checked
    ? [...selectedOrgIds.value, id]
    : selectedOrgIds.value.filter((value) => value !== id);
  if (checked && quotaCounts[id] === undefined) quotaCounts[id] = 1;
}
function updateQuota(id: string, count: number) {
  quotaCounts[id] = count;
}
async function create() {
  if (!canSubmit.value) return;
  error.value = "";
  try {
    const payload = {
      ...form,
      question_ids: selectedIds.value,
      eligible_org_units: selectedOrgIds.value.map((org_unit_id) => ({
        org_unit_id, eligible_count: quotaCounts[org_unit_id],
      })),
    };
    if (editingId.value) {
      await apiRequest(`/papers/${editingId.value}`, "PATCH", payload);
      message.value = "บันทึกการแก้ไข Draft และ Audit Log แล้ว";
    } else {
      const { change_summary: _summary, ...createPayload } = payload;
      await apiRequest("/papers", "POST", createPayload);
      message.value = "สร้าง Exam Creation พร้อมเกณฑ์ผ่านและ quota แล้ว";
    }
    resetForm();
    await loadPapers();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "สร้าง Exam Creation ไม่สำเร็จ";
  }
}

function resetForm() {
  editingId.value = null;
  Object.assign(form, { title: "", org_unit_id: "", subject_id: "", desired_question_count: 10, variant_count: 1, passing_percentage: 60, default_duration_minutes: 60, question_selection_mode: "fixed_set", pool_criteria: null, change_summary: "" });
  selectedIds.value = [];
  selectedOrgIds.value = [];
  Object.keys(quotaCounts).forEach((key) => delete quotaCounts[key]);
}
async function startEdit(paper: Paper) {
  error.value = "";
  try {
    const detail = await apiGet<PaperEdit>(`/papers/${paper.id}/edit`);
    editingId.value = paper.id;
    preserveQuestionSelection.value = true;
    Object.assign(form, {
      title: detail.title, org_unit_id: detail.org_unit_id, subject_id: detail.subject_id ?? "",
      desired_question_count: detail.desired_question_count, variant_count: detail.variant_count,
      passing_percentage: detail.passing_percentage, default_duration_minutes: detail.default_duration_minutes,
      question_selection_mode: detail.question_selection_mode, pool_criteria: detail.pool_criteria,
      change_summary: "",
    });
    await loadQuestions();
    selectedIds.value = detail.question_ids;
    selectedOrgIds.value = detail.eligible_org_units.map((item) => item.org_unit_id);
    Object.keys(quotaCounts).forEach((key) => delete quotaCounts[key]);
    detail.eligible_org_units.forEach((item) => { quotaCounts[item.org_unit_id] = item.eligible_count; });
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "โหลด Draft เพื่อแก้ไขไม่สำเร็จ"; }
  finally { preserveQuestionSelection.value = false; }
}
function requestRevision(paper: Paper) {
  revisionPending.value = paper; revisionTitle.value = ""; revisionSummary.value = "";
}
async function createRevision() {
  if (!revisionPending.value || revisionSummary.value.trim().length < 3) return;
  statusBusy.value = true;
  try {
    const revision = await apiRequest<Paper>(`/papers/${revisionPending.value.id}/revisions`, "POST", {
      title: revisionTitle.value.trim() || undefined, change_summary: revisionSummary.value.trim(),
    });
    revisionPending.value = null;
    message.value = `สร้าง Revision ${revision.revision_number} เป็น Draft แล้ว`;
    await loadPapers();
    await startEdit(revision);
  } catch (cause) { error.value = cause instanceof Error ? cause.message : "สร้าง Revision ไม่สำเร็จ"; }
  finally { statusBusy.value = false; }
}

async function loadPapers() {
  papers.value = await apiGet<Paper[]>("/papers");
}
function requestStatus(paper: Paper, status: PaperLifecycleStatus) {
  pendingStatus.value = { paper, status };
}
async function confirmStatus() {
  if (!pendingStatus.value) return;
  statusBusy.value = true;
  error.value = "";
  try {
    const { paper, status } = pendingStatus.value;
    await apiRequest(`/papers/${paper.id}/status`, "PATCH", { status });
    message.value = `เปลี่ยนสถานะ “${paper.title}” เป็น ${statusLabels[status]} แล้ว`;
    pendingStatus.value = null;
    await loadPapers();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "เปลี่ยนสถานะไม่สำเร็จ";
  } finally { statusBusy.value = false; }
}

watch(() => form.subject_id, loadQuestions);
onMounted(loadBase);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Exam Author" title="สร้าง Exam Creation" description="กำหนดข้อสอบ ระยะเวลา เกณฑ์ผ่าน และจำนวนผู้มีสิทธิ์ต่อหน่วยงาน" />
    <AppAlert v-if="message" type="success">{{ message }}</AppAlert>
    <AppAlert v-if="error" type="error">{{ error }}</AppAlert>

    <section class="card mb-6 border border-base-300 bg-base-100 shadow-sm">
      <div class="card-body">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="card-title">Exam Creation ที่สร้างไว้</h2>
            <p class="text-sm text-base-content/60">Draft แก้ไขเตรียมการได้, เปิดใช้งานเพื่อสร้าง Exam Window และปิดใช้งานเมื่อต้องการหยุดใช้</p>
          </div>
          <span class="badge badge-outline">{{ papers.length }} รายการ</span>
        </div>
        <div v-if="papersLoading" class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 3" :key="index" class="skeleton h-36 w-full"></div>
        </div>
        <div v-else-if="!papers.length" class="alert">ยังไม่มี Exam Creation ในขอบเขตที่คุณดูแล</div>
        <div v-else class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="paper in papers" :key="paper.id" class="rounded-box border border-base-300 p-4">
            <div class="flex items-start justify-between gap-3">
              <h3 class="font-semibold">{{ paper.title }}</h3>
              <span class="badge shrink-0" :class="statusClasses[paper.status]">{{ statusLabels[paper.status] }}</span>
            </div>
            <dl class="my-4 grid grid-cols-2 gap-2 text-sm">
              <div><dt class="text-base-content/60">Revision</dt><dd class="font-medium">{{ paper.revision_number }}</dd></div>
              <div><dt class="text-base-content/60">การใช้งาน</dt><dd class="font-medium">{{ paper.window_count }} รอบ / {{ paper.session_count }} session</dd></div>
              <div><dt class="text-base-content/60">ระยะเวลา</dt><dd class="font-medium">{{ paper.default_duration_minutes }} นาที</dd></div>
              <div><dt class="text-base-content/60">เกณฑ์ผ่าน</dt><dd class="font-medium">{{ paper.passing_percentage ?? "—" }}%</dd></div>
              <div><dt class="text-base-content/60">คำถาม</dt><dd class="font-medium">{{ paper.question_count }} / {{ paper.desired_question_count }} ข้อ</dd></div>
              <div><dt class="text-base-content/60">หน่วยงาน quota</dt><dd class="font-medium">{{ paper.allowed_org_unit_count }} หน่วย</dd></div>
            </dl>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <PaperEditActions :can-edit="paper.can_edit" :can-revise="paper.can_revise" :revision-number="paper.revision_number" @edit="startEdit(paper)" @revise="requestRevision(paper)" />
              <PaperLifecycleActions :status="paper.status" @request="requestStatus(paper, $event)" />
            </div>
          </article>
        </div>
      </div>
    </section>

    <form class="space-y-6" @submit.prevent="create">
      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <div class="flex items-center justify-between gap-3"><h2 class="card-title">{{ editingId ? 'แก้ไข Draft' : 'ข้อมูลการสร้างข้อสอบ' }}</h2><button v-if="editingId" class="btn btn-ghost btn-sm" type="button" @click="resetForm">ยกเลิกการแก้ไข</button></div>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <label class="form-control"><span class="label-text">ชื่อ Exam Creation</span><input v-model="form.title" class="input input-bordered" required /></label>
          <label class="form-control"><span class="label-text">รายวิชา</span><select v-model="form.subject_id" class="select select-bordered" required><option disabled value="">เลือกรายวิชา</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} — {{ subject.name }}</option></select></label>
          <label class="form-control"><span class="label-text">หน่วยงานเจ้าของ</span><select v-model="form.org_unit_id" class="select select-bordered" required><option disabled value="">เลือกหน่วยงาน</option><option v-for="unit in orgUnits" :key="unit.id" :value="unit.id">{{ unit.name }}</option></select></label>
          <label class="form-control"><span class="label-text">จำนวนข้อ</span><input v-model.number="form.desired_question_count" class="input input-bordered" type="number" min="1" max="200" required /></label>
          <label class="form-control"><span class="label-text">จำนวน variants</span><input v-model.number="form.variant_count" class="input input-bordered" type="number" min="1" max="20" required /></label>
          <label class="form-control"><span class="label-text">เกณฑ์ผ่าน (%)</span><input v-model.number="form.passing_percentage" class="input input-bordered" type="number" min="0" max="100" step="0.01" required /></label>
          <label class="form-control"><span class="label-text">ระยะเวลาทำข้อสอบ (นาที)</span><input v-model.number="form.default_duration_minutes" class="input input-bordered" type="number" min="1" max="600" required /><span class="label-text-alt mt-1 text-base-content/60">Exam Window จะใช้ค่านี้เป็นค่าเริ่มต้น</span></label>
          <label class="form-control"><span class="label-text">รูปแบบเลือกคำถาม</span><select v-model="form.question_selection_mode" class="select select-bordered"><option value="fixed_set">Fixed set</option><option value="random_pool">Random pool</option></select></label>
          <label v-if="editingId" class="form-control md:col-span-2"><span class="label-text">สรุปการแก้ไข</span><input v-model="form.change_summary" class="input input-bordered" minlength="3" maxlength="500" placeholder="ระบุสิ่งที่เปลี่ยนเพื่อบันทึก Audit" required /></label>
        </div>
      </div></section>

      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <h2 class="card-title">Quota ผู้มีสิทธิ์สอบรายหน่วยงาน</h2>
        <p class="text-sm text-base-content/60">เลือกหน่วยงานตามโครงสร้าง ระบบจะป้องกันโควต้าหน่วยแม่และหน่วยลูกซ้อนกันก่อนส่งข้อมูล</p>
        <OrgQuotaTree
          :units="orgUnits"
          :selected-ids="selectedOrgIds"
          :quota-counts="quotaCounts"
          @toggle="toggleOrganization"
          @update-quota="updateQuota"
        />
      </div></section>

      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <div class="flex flex-wrap items-center justify-between gap-3"><h2 class="card-title">เลือกคำถาม</h2><span class="badge" :class="selectedIds.length >= form.desired_question_count ? 'badge-success' : 'badge-warning'">{{ selectedIds.length }} / {{ form.desired_question_count }}</span></div>
        <input v-model="search" class="input input-bordered" placeholder="ค้นหาคำถาม" />
        <span v-if="loading" class="loading loading-spinner loading-lg self-center"></span>
        <div v-else-if="!questions.length" class="alert">เลือกรายวิชาที่มีคำถามพร้อมใช้งาน</div>
        <div v-else class="grid max-h-[32rem] gap-3 overflow-y-auto">
          <label v-for="question in filteredQuestions" :key="question.id" class="rounded-box flex cursor-pointer gap-3 border border-base-300 p-3"><input v-model="selectedIds" class="checkbox checkbox-primary" type="checkbox" :value="question.id" /><span>{{ question.content }}</span></label>
        </div>
      </div></section>
      <div class="flex justify-end"><button class="btn btn-primary btn-lg" type="submit" :disabled="!canSubmit">{{ editingId ? 'บันทึก Draft' : 'สร้าง Exam Creation' }}</button></div>
    </form>
    <ConfirmModal
      :open="Boolean(pendingStatus)"
      :title="confirmation.title"
      :message="confirmation.message"
      :confirm-label="confirmation.label"
      cancel-label="ยกเลิก"
      :busy="statusBusy"
      @confirm="confirmStatus"
      @cancel="pendingStatus = null"
    />
    <ConfirmModal
      :open="Boolean(revisionPending)"
      title="สร้าง Revision ใหม่"
      :message="revisionPending ? `ระบบจะคัดลอก “${revisionPending.title}” เป็น Draft ใหม่ โดยไม่เปลี่ยนข้อสอบและผลสอบเดิม` : ''"
      confirm-label="สร้าง Revision"
      cancel-label="ยกเลิก"
      :busy="statusBusy"
      :confirm-disabled="revisionSummary.trim().length < 3"
      @confirm="createRevision"
      @cancel="revisionPending = null"
    >
      <div class="grid gap-3"><label class="form-control"><span class="label-text">ชื่อฉบับใหม่ (ไม่บังคับ)</span><input v-model="revisionTitle" class="input input-bordered" maxlength="255" /></label><label class="form-control"><span class="label-text">เหตุผล/สรุปการเปลี่ยนแปลง *</span><textarea v-model="revisionSummary" class="textarea textarea-bordered" minlength="3" maxlength="500"></textarea></label></div>
    </ConfirmModal>
  </PageContainer>
</template>
