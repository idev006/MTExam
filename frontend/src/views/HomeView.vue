<script setup lang="ts">
import { computed, ref } from "vue";

import AppAlert from "@/components/feedback/AppAlert.vue";
import AppToast from "@/components/feedback/AppToast.vue";
import EmployeeTable from "@/components/employees/EmployeeTable.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
import { useEmployees } from "@/composables/useEmployees";
import { useHealth } from "@/composables/useHealth";

const { health, errorMessage, isLoading: healthLoading, loadHealth } = useHealth();
const { employees, search, isLoading: employeesLoading, filteredEmployees, refresh } = useEmployees();
const toastVisible = ref(false);
const toastMessage = ref("");

const activeCount = computed(() => employees.value.filter((employee) => employee.status === "active").length);
const changedCount = computed(() => employees.value.filter((employee) => employee.status === "changed").length);

function showToast(message: string) {
  toastMessage.value = message;
  toastVisible.value = true;
}

async function refreshData() {
  await Promise.all([loadHealth(), refresh()]);
  showToast("อัปเดตข้อมูลล่าสุดแล้ว");
}
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="ภาพรวมระบบ" title="ยินดีต้อนรับสู่ MTExam" description="ติดตามบุคลากร สถานะระบบ และการนำเข้าข้อมูลจาก CSV ได้จากหน้าจอเดียว">
      <template #actions><button class="btn btn-primary" type="button" @click="refreshData"><span aria-hidden="true">↻</span> อัปเดตข้อมูล</button></template>
    </PageHeader>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="บุคลากรทั้งหมด" :value="String(employees.length)" hint="จากรอบนำเข้าล่าสุด" icon="♙" tone="primary" />
      <StatCard label="กำลังปฏิบัติงาน" :value="String(activeCount)" hint="สถานะปกติในระบบ" icon="✓" tone="success" />
      <StatCard label="รอตรวจสอบ" :value="String(changedCount)" hint="รายการมีการเปลี่ยนแปลง" icon="!" tone="warning" />
      <StatCard label="รอบนำเข้าล่าสุด" value="วันนี้" hint="เวลา 09:42 น." icon="↥" tone="info" />
    </div>

    <div class="mt-6 grid gap-6 lg:grid-cols-[1fr_20rem]">
      <section class="card border border-base-300 bg-base-100 shadow-sm">
        <div class="card-body p-0">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-base-300 p-5">
            <div><h2 class="card-title">บุคลากรล่าสุด</h2><p class="text-sm text-base-content/60">ข้อมูลตัวอย่างจาก employee table</p></div>
            <label class="input input-bordered flex items-center gap-2"><span aria-hidden="true">⌕</span><input v-model="search" class="w-40" type="search" placeholder="ค้นหาชื่อหรือหน่วยงาน" /></label>
          </div>
          <EmployeeTable :employees="filteredEmployees" :loading="employeesLoading" />
        </div>
      </section>

      <aside class="space-y-6">
        <section class="card border border-primary/20 bg-primary text-primary-content shadow-sm"><div class="card-body"><div class="flex items-center justify-between"><h2 class="card-title">นำเข้าข้อมูล CSV</h2><span class="text-2xl" aria-hidden="true">↥</span></div><p class="text-sm opacity-80">เพิ่มข้อมูลหรือปรับปรุงบุคลากรเป็นรอบ โดยระบบจะตรวจสอบรายการเพิ่ม ลด และเปลี่ยนแปลง</p><button class="btn mt-2 border-0 bg-white/20 text-white hover:bg-white/30" type="button" @click="showToast('POC: เตรียมหน้าจอนำเข้า CSV แล้ว')">เริ่มนำเข้าไฟล์</button></div></section>
        <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="card-title text-base">สถานะ API</h2><AppAlert v-if="healthLoading"><span class="loading loading-spinner loading-xs"></span> กำลังตรวจสอบ</AppAlert><AppAlert v-else-if="health" type="success"><div><p class="font-semibold">พร้อมใช้งาน</p><p class="text-xs">{{ health.app_name }} · {{ health.database }}</p></div></AppAlert><AppAlert v-else type="error"><div class="grow"><p class="font-semibold">เชื่อมต่อไม่ได้</p><p class="text-xs">{{ errorMessage }}</p></div><button class="btn btn-xs" type="button" @click="loadHealth">ลองใหม่</button></AppAlert></div></section>
      </aside>
    </div>
    <AppToast :visible="toastVisible" :message="toastMessage" type="success" @dismiss="toastVisible = false" />
  </PageContainer>
</template>
