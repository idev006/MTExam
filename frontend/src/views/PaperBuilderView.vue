<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface Subject { id: string; code: string; name: string }
const subjects = ref<Subject[]>([]);
const form = ref({ title: "", org_unit_id: "", subject_id: "", question_ids: "", variant_count: 1 });
const message = ref("");
async function load() { subjects.value = await apiGet<Subject[]>("/question-banks/subjects"); }
async function create() { await apiRequest("/papers", "POST", { ...form.value, question_ids: form.value.question_ids.split(/[,\n]/).map((value) => value.trim()).filter(Boolean) }); message.value = "สร้าง Exam Creation และชุดข้อสอบแล้ว"; }
onMounted(load);
</script>

<template><PageContainer><PageHeader eyebrow="Exam Author" title="สร้าง Exam Creation" description="การสร้างแต่ละครั้งจะมีรายวิชาและจำนวนชุดข้อสอบของตัวเอง เพื่อแยกสถิติอย่างถูกต้อง" /><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body max-w-2xl"><AppAlert v-if="message" type="success">{{ message }}</AppAlert><form class="space-y-4" @submit.prevent="create"><input v-model="form.title" class="input input-bordered w-full" placeholder="ชื่อการสร้างข้อสอบ" required /><select v-model="form.subject_id" class="select select-bordered w-full" required><option disabled value="">เลือกรายวิชา</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} — {{ subject.name }}</option></select><input v-model="form.org_unit_id" class="input input-bordered w-full" placeholder="Org Unit UUID" required /><textarea v-model="form.question_ids" class="textarea textarea-bordered h-32 w-full" placeholder="Question UUID คั่นด้วย comma หรือขึ้นบรรทัดใหม่" required></textarea><label class="form-control"><span class="label-text">จำนวนชุดข้อสอบ (Variants)</span><input v-model.number="form.variant_count" class="range range-primary" type="range" min="1" max="20" /><span>{{ form.variant_count }} ชุด</span></label><button class="btn btn-primary" type="submit">สร้าง Exam Creation</button></form></div></section></PageContainer></template>
