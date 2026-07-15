<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";
interface Subject { id: string; code: string; name: string }
interface OrgUnit { id: string; code: string; name: string; level: string }
const subjects = ref<Subject[]>([]); const orgUnits = ref<OrgUnit[]>([]);
const form = ref({ title: "", org_unit_id: "", subject_id: "", question_ids: "", desired_question_count: 1, variant_count: 1, allowed_org_unit_ids: [] as string[] });
const message = ref("");
async function load() { [subjects.value, orgUnits.value] = await Promise.all([apiGet<Subject[]>("/question-banks/subjects"), apiGet<OrgUnit[]>("/org-units")]); }
async function create() { await apiRequest("/papers", "POST", { ...form.value, question_ids: form.value.question_ids.split(/[,\n]/).map((value) => value.trim()).filter(Boolean) }); message.value = "สร้าง Exam Creation และชุดข้อสอบแล้ว"; }
onMounted(load);
</script>
<template><PageContainer><PageHeader eyebrow="Exam Author" title="สร้าง Exam Creation" description="กำหนดรายวิชา จำนวนข้อ ชุดข้อสอบ และหน่วยงานผู้มีสิทธิ์สอบ" /><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body max-w-3xl"><AppAlert v-if="message" type="success">{{ message }}</AppAlert><form class="space-y-4" @submit.prevent="create"><input v-model="form.title" class="input input-bordered w-full" placeholder="ชื่อการสร้างข้อสอบ" required /><select v-model="form.subject_id" class="select select-bordered w-full" required><option disabled value="">เลือกรายวิชา</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} — {{ subject.name }}</option></select><label class="form-control"><span class="label-text">จำนวนข้อที่ต้องการ</span><input v-model.number="form.desired_question_count" class="input input-bordered" type="number" min="1" max="200" required /></label><input v-model="form.org_unit_id" class="input input-bordered w-full" placeholder="Org Unit UUID สำหรับเจ้าของข้อสอบ" required /><fieldset class="rounded-box border border-base-300 p-3"><legend class="px-1 font-semibold">หน่วยระดับกองบังคับการที่อนุญาตให้ทำข้อสอบ</legend><label v-for="unit in orgUnits.filter((item) => item.level === 'bureau')" :key="unit.id" class="label cursor-pointer justify-start gap-3"><input v-model="form.allowed_org_unit_ids" class="checkbox checkbox-primary" type="checkbox" :value="unit.id" /><span>{{ unit.name }}</span></label></fieldset><textarea v-model="form.question_ids" class="textarea textarea-bordered h-32 w-full" placeholder="Question UUID คั่นด้วย comma หรือขึ้นบรรทัดใหม่" required></textarea><label class="form-control"><span class="label-text">จำนวนชุดข้อสอบ (Variants)</span><input v-model.number="form.variant_count" class="range range-primary" type="range" min="1" max="20" /><span>{{ form.variant_count }} ชุด</span></label><button class="btn btn-primary" type="submit">สร้าง Exam Creation</button></form></div></section></PageContainer></template>
