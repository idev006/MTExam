<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface Bank { id: string; name: string; status: string }
const banks = ref<Bank[]>([]); const form = ref({ name: "", owner_org_unit_id: "", is_shared: false }); const message = ref("");
async function load() { banks.value = await apiGet<Bank[]>("/question-banks"); }
async function create() { await apiRequest<Bank>("/question-banks", "POST", form.value); message.value = "สร้าง question bank แล้ว"; await load(); }
async function publish(id: string) { await apiRequest<Bank>(`/question-banks/${id}/publish`, "POST"); await load(); }
onMounted(load);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Exam Author" title="จัดการ Question Bank" description="สร้างและเผยแพร่คลังข้อสอบ" />
    <div class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><form class="grid gap-3 md:grid-cols-4" @submit.prevent="create"><input v-model="form.name" class="input input-bordered" placeholder="ชื่อคลังข้อสอบ" required /><input v-model="form.owner_org_unit_id" class="input input-bordered" placeholder="Org Unit UUID" required /><label class="label cursor-pointer gap-2"><input v-model="form.is_shared" class="toggle toggle-primary" type="checkbox" /> Shared</label><button class="btn btn-primary" type="submit">สร้างคลังข้อสอบ</button></form></div></div>
    <AppAlert v-if="message" type="success">{{ message }}</AppAlert>
    <div class="mt-6 card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><table class="table"><thead><tr><th>ชื่อ</th><th>สถานะ</th><th></th></tr></thead><tbody><tr v-for="bank in banks" :key="bank.id"><td>{{ bank.name }}</td><td>{{ bank.status }}</td><td><button v-if="bank.status === 'draft'" class="btn btn-primary btn-xs" type="button" @click="publish(bank.id)">เผยแพร่</button></td></tr></tbody></table></div></div>
  </PageContainer>
</template>
