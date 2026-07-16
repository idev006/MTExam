<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppToast from "@/components/feedback/AppToast.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet, apiRequest } from "@/api/client";

interface User { id: string; username: string; full_name: string; role: string; status: string }
interface OrgUnit { id: string; code: string; name: string; level: string; status: string }
const users = ref<User[]>([]); const units = ref<OrgUnit[]>([]); const error = ref(""); const toast = ref(false);
const form = ref({ username: "", password: "", full_name: "", role: "examinee" });
const selectedUser = ref<User | null>(null); const selectedScope = ref<string[]>([]);
async function load() { try { [users.value, units.value] = await Promise.all([apiGet<User[]>("/admin/users"), apiGet<OrgUnit[]>("/org-units")]); } catch (e) { error.value = e instanceof Error ? e.message : "โหลดข้อมูลไม่สำเร็จ"; } }
async function create() { await apiRequest<User>("/admin/users", "POST", form.value); form.value = { username: "", password: "", full_name: "", role: "examinee" }; toast.value = true; await load(); }
async function deactivate(id: string) { await apiRequest<User>(`/admin/users/${id}/deactivate`, "POST"); await load(); }
async function editScope(user: User) { selectedUser.value = user; const response = await apiGet<{ org_unit_ids: string[] }>(`/admin/users/${user.id}/scope`); selectedScope.value = response.org_unit_ids; }
async function saveScope() { if (!selectedUser.value) return; await apiRequest(`/admin/users/${selectedUser.value.id}/scope`, "PUT", { org_unit_ids: selectedScope.value }); toast.value = true; }
async function updateRole(event: Event, user: User) { const role = (event.target as HTMLSelectElement).value; await apiRequest(`/admin/users/${user.id}`, "PATCH", { role }); toast.value = true; await load(); }
onMounted(load);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="ผู้ดูแลระบบ" title="จัดการผู้ใช้ สิทธิ์ และหน่วยงาน" description="บริหาร role สถานะบัญชี และขอบเขตหน่วยงานผ่านระบบโดยตรง">
      <template #actions><RouterLink class="btn btn-ghost" to="/">กลับหน้าหลัก</RouterLink></template>
    </PageHeader>
    <AppAlert v-if="error" type="error">{{ error }}</AppAlert>
    <div class="grid gap-6 lg:grid-cols-[20rem_1fr]">
      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body">
        <h2 class="card-title text-base">สร้างผู้ใช้</h2>
        <form class="space-y-3" @submit.prevent="create">
          <input v-model="form.username" class="input input-bordered w-full" placeholder="username" required />
          <input v-model="form.password" class="input input-bordered w-full" type="password" placeholder="password อย่างน้อย 12 ตัว" required />
          <input v-model="form.full_name" class="input input-bordered w-full" placeholder="ชื่อ-นามสกุล" required />
          <select v-model="form.role" class="select select-bordered w-full"><option value="super_admin">super_admin</option><option value="exam_author">exam_author</option><option value="examinee">examinee</option><option value="viewer">viewer</option></select>
          <button class="btn btn-primary w-full" type="submit">สร้างผู้ใช้</button>
        </form>
      </div></section>
      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body overflow-x-auto">
        <h2 class="card-title text-base">ผู้ใช้ในระบบ</h2>
        <table class="table"><thead><tr><th>Username</th><th>ชื่อ</th><th>Role</th><th>สถานะ</th><th>จัดการ</th></tr></thead>
          <tbody><tr v-for="item in users" :key="item.id"><td>{{ item.username }}</td><td>{{ item.full_name }}</td><td><select class="select select-bordered select-sm" :value="item.role" @change="updateRole($event, item)"><option value="super_admin">super_admin</option><option value="exam_author">exam_author</option><option value="examinee">examinee</option><option value="viewer">viewer</option></select></td><td>{{ item.status }}</td><td class="flex gap-2"><button class="btn btn-info btn-xs" type="button" @click="editScope(item)">หน่วยงาน</button><button v-if="item.status === 'active'" class="btn btn-error btn-xs" type="button" @click="deactivate(item.id)">ปิดใช้งาน</button></td></tr></tbody>
        </table>
      </div></section>
    </div>
    <dialog class="modal" :class="{ 'modal-open': selectedUser }"><div class="modal-box"><h3 class="font-bold text-lg">หน่วยงานของ {{ selectedUser?.username }}</h3><div class="max-h-80 overflow-y-auto space-y-2 py-4"><label v-for="unit in units" :key="unit.id" class="label cursor-pointer justify-start gap-3"><input v-model="selectedScope" class="checkbox checkbox-primary" type="checkbox" :value="unit.id" /><span>{{ unit.name }} ({{ unit.level }})</span></label></div><div class="modal-action"><button class="btn" type="button" @click="selectedUser = null">ยกเลิก</button><button class="btn btn-primary" type="button" @click="saveScope">บันทึก</button></div></div></dialog>
    <AppToast :visible="toast" message="บันทึกข้อมูลสำเร็จ" type="success" @dismiss="toast = false" />
  </PageContainer>
</template>
