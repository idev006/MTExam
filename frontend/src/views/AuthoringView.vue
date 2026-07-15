<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface Bank { id: string; name: string; status: string; subject_id?: string }
interface Subject { id: string; code: string; name: string; status: string }
const banks = ref<Bank[]>([]);
const subjects = ref<Subject[]>([]);
const form = ref({ name: "", owner_org_unit_id: "", subject_id: "", is_shared: false });
const message = ref("");
async function load() { [banks.value, subjects.value] = await Promise.all([apiGet<Bank[]>("/question-banks"), apiGet<Subject[]>("/question-banks/subjects")]); }
async function create() { await apiRequest<Bank>("/question-banks", "POST", form.value); message.value = "สร้างคลังข้อสอบแล้ว"; await load(); }
async function publish(id: string) { await apiRequest<Bank>(`/question-banks/${id}/publish`, "POST"); await load(); }
onMounted(load);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Exam Author" title="จัดการคลังข้อสอบ" description="คลังข้อสอบต้องผูกกับรายวิชาเพื่อการจัดกลุ่มและรายงานสถิติ" />
    <div class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><form class="grid gap-3 md:grid-cols-5" @submit.prevent="create"><input v-model="form.name" class="input input-bordered" placeholder="ชื่อคลังข้อสอบ" required /><input v-model="form.owner_org_unit_id" class="input input-bordered" placeholder="Org Unit UUID" required /><select v-model="form.subject_id" class="select select-bordered" required><option disabled value="">เลือกรายวิชา</option><option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.code }} — {{ subject.name }}</option></select><label class="label cursor-pointer gap-2"><input v-model="form.is_shared" class="toggle toggle-primary" type="checkbox" /> Shared</label><button class="btn btn-primary" type="submit">สร้างคลังข้อสอบ</button></form></div></div>
    <AppAlert v-if="message" type="success">{{ message }}</AppAlert>
    <div class="mt-6 card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><div class="overflow-x-auto"><table class="table"><thead><tr><th>คลังข้อสอบ</th><th>รายวิชา</th><th>สถานะ</th><th></th></tr></thead><tbody><tr v-for="bank in banks" :key="bank.id"><td>{{ bank.name }}</td><td>{{ subjects.find((subject) => subject.id === bank.subject_id)?.name || "-" }}</td><td>{{ bank.status }}</td><td><button v-if="bank.status === 'draft'" class="btn btn-primary btn-xs" type="button" @click="publish(bank.id)">เผยแพร่</button></td></tr></tbody></table></div></div></div>
  </PageContainer>
</template>
