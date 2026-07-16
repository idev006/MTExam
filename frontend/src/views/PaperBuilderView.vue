<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface Subject { id: string; code: string; name: string }
interface OrgUnit { id: string; name: string; level: string; status: string }
interface Question { id: string; content: string; difficulty: string | null; bank_name: string }

const subjects = ref<Subject[]>([]);
const orgUnits = ref<OrgUnit[]>([]);
const questions = ref<Question[]>([]);
const selectedIds = ref<string[]>([]);
const selectedOrgIds = ref<string[]>([]);
const quotaCounts = reactive<Record<string, number>>({});
const search = ref("");
const message = ref("");
const error = ref("");
const loading = ref(false);
const form = reactive({
  title: "", org_unit_id: "", subject_id: "", desired_question_count: 10,
  variant_count: 1, passing_percentage: 60,
});

const filteredQuestions = computed(() => questions.value.filter((question) =>
  !search.value || `${question.content} ${question.bank_name}`.toLowerCase().includes(search.value.toLowerCase()),
));
const canSubmit = computed(() => Boolean(
  form.title && form.subject_id && form.org_unit_id && selectedOrgIds.value.length
  && selectedIds.value.length >= form.desired_question_count
  && form.passing_percentage >= 0 && form.passing_percentage <= 100
  && selectedOrgIds.value.every((id) => Number.isInteger(quotaCounts[id]) && quotaCounts[id] >= 0),
));

async function loadBase() {
  [subjects.value, orgUnits.value] = await Promise.all([
    apiGet<Subject[]>("/question-banks/subjects"), apiGet<OrgUnit[]>("/org-units"),
  ]);
}
async function loadQuestions() {
  if (!form.subject_id) { questions.value = []; return; }
  loading.value = true;
  try {
    questions.value = await apiGet<Question[]>(`/question-banks/questions?subject_id=${form.subject_id}`);
    selectedIds.value = [];
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
async function create() {
  if (!canSubmit.value) return;
  error.value = "";
  try {
    await apiRequest("/papers", "POST", {
      ...form,
      question_ids: selectedIds.value,
      eligible_org_units: selectedOrgIds.value.map((org_unit_id) => ({
        org_unit_id, eligible_count: quotaCounts[org_unit_id],
      })),
    });
    message.value = "สร้าง Exam Creation พร้อมเกณฑ์ผ่านและ quota แล้ว";
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "สร้าง Exam Creation ไม่สำเร็จ";
  }
}

watch(() => form.subject_id, loadQuestions);
onMounted(loadBase);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Exam Author" title="สร้าง Exam Creation" description="กำหนดข้อสอบ เกณฑ์ผ่าน และจำนวนผู้มีสิทธิ์ต่อหน่วยงาน" />
    <AppAlert v-if="message" type="success">{{ message }}</AppAlert>
    <AppAlert v-if="error" type="error">{{ error }}</AppAlert>
    <form class="space-y-6" @submit.prevent="create">
      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <h2 class="card-title">ข้อมูลการสร้างข้อสอบ</h2>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <label class="form-control"><span class="label-text">ชื่อ Exam Creation</span><input v-model="form.title" class="input input-bordered" required /></label>
          <label class="form-control"><span class="label-text">รายวิชา</span><select v-model="form.subject_id" class="select select-bordered" required><option disabled value="">เลือกรายวิชา</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} — {{ subject.name }}</option></select></label>
          <label class="form-control"><span class="label-text">หน่วยงานเจ้าของ</span><select v-model="form.org_unit_id" class="select select-bordered" required><option disabled value="">เลือกหน่วยงาน</option><option v-for="unit in orgUnits" :key="unit.id" :value="unit.id">{{ unit.name }}</option></select></label>
          <label class="form-control"><span class="label-text">จำนวนข้อ</span><input v-model.number="form.desired_question_count" class="input input-bordered" type="number" min="1" max="200" required /></label>
          <label class="form-control"><span class="label-text">จำนวน variants</span><input v-model.number="form.variant_count" class="input input-bordered" type="number" min="1" max="20" required /></label>
          <label class="form-control"><span class="label-text">เกณฑ์ผ่าน (%)</span><input v-model.number="form.passing_percentage" class="input input-bordered" type="number" min="0" max="100" step="0.01" required /></label>
        </div>
      </div></section>

      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <h2 class="card-title">Quota ผู้มีสิทธิ์สอบรายหน่วยงาน</h2>
        <p class="text-sm text-base-content/60">ห้ามเลือกหน่วยแม่และหน่วยลูกซ้อนกัน ระบบจะจำกัดจำนวนผู้เริ่มสอบตาม quota</p>
        <div class="grid gap-3 md:grid-cols-2">
          <div v-for="unit in orgUnits" :key="unit.id" class="rounded-box border border-base-300 p-3">
            <label class="flex cursor-pointer items-center gap-3"><input class="checkbox checkbox-primary" type="checkbox" :checked="selectedOrgIds.includes(unit.id)" @change="toggleOrganization(unit.id, ($event.target as HTMLInputElement).checked)" /><span class="flex-1">{{ unit.name }}</span><span class="badge badge-ghost">{{ unit.level }}</span></label>
            <label v-if="selectedOrgIds.includes(unit.id)" class="form-control mt-3"><span class="label-text">จำนวนผู้มีสิทธิ์</span><input v-model.number="quotaCounts[unit.id]" class="input input-bordered" type="number" min="0" required /></label>
          </div>
        </div>
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
      <div class="flex justify-end"><button class="btn btn-primary btn-lg" type="submit" :disabled="!canSubmit">สร้าง Exam Creation</button></div>
    </form>
  </PageContainer>
</template>
