<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppToast from "@/components/feedback/AppToast.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface User { id: string; username: string; full_name: string; role: string; status: string }
const users = ref<User[]>([]); const error = ref(""); const toast = ref(false); const form = ref({ username: "", password: "", full_name: "", role: "examinee" });
async function load() { try { users.value = await apiGet<User[]>("/admin/users"); } catch (e) { error.value = e instanceof Error ? e.message : "โหลดผู้ใช้ไม่สำเร็จ"; } }
async function create() { await apiRequest<User>("/admin/users", "POST", form.value); form.value = { username: "", password: "", full_name: "", role: "examinee" }; toast.value = true; await load(); }
async function deactivate(id: string) { await apiRequest<User>(`/admin/users/${id}/deactivate`, "POST"); await load(); }
onMounted(load);
</script>
<template><PageContainer><PageHeader eyebrow="ผู้ดูแลระบบ" title="จัดการผู้ใช้และสิทธิ์" description="สร้าง ปิดใช้งาน และตรวจสอบ role ของผู้ใช้"><template #actions><RouterLink class="btn btn-ghost" to="/">กลับหน้าหลัก</RouterLink></template></PageHeader><AppAlert v-if="error" type="error">{{ error }}</AppAlert><div class="grid gap-6 lg:grid-cols-[20rem_1fr]"><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="card-title text-base">สร้างผู้ใช้</h2><form class="space-y-3" @submit.prevent="create"><input v-model="form.username" class="input input-bordered w-full" placeholder="username" required /><input v-model="form.password" class="input input-bordered w-full" type="password" placeholder="password อย่างน้อย 8 ตัว" required /><input v-model="form.full_name" class="input input-bordered w-full" placeholder="ชื่อ-นามสกุล" required /><select v-model="form.role" class="select select-bordered w-full"><option value="super_admin">super_admin</option><option value="exam_author">exam_author</option><option value="examinee">examinee</option><option value="viewer">viewer</option></select><button class="btn btn-primary w-full" type="submit">สร้างผู้ใช้</button></form></div></section><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body overflow-x-auto"><h2 class="card-title text-base">ผู้ใช้ในระบบ</h2><table class="table"><thead><tr><th>Username</th><th>ชื่อ</th><th>Role</th><th>สถานะ</th><th></th></tr></thead><tbody><tr v-for="item in users" :key="item.id"><td>{{ item.username }}</td><td>{{ item.full_name }}</td><td><span class="badge badge-primary">{{ item.role }}</span></td><td>{{ item.status }}</td><td><button v-if="item.status === 'active'" class="btn btn-error btn-xs" type="button" @click="deactivate(item.id)">ปิดใช้งาน</button></td></tr></tbody></table></div></section></div><AppToast :visible="toast" message="สร้างผู้ใช้สำเร็จ" type="success" @dismiss="toast = false" /></PageContainer></template>
