<script setup lang="ts">
import { ref } from "vue";

import AppToast from "@/components/feedback/AppToast.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import ThemeSelector from "@/components/settings/ThemeSelector.vue";

const sessionMode = ref("role");
const maxSessions = ref(3);
const idleTimeout = ref(30);
const strictImport = ref(true);
const toastVisible = ref(false);

function saveSettings() {
  toastVisible.value = true;
}
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="ผู้ดูแลระบบ" title="การตั้งค่าระบบ" description="ตั้งค่าการใช้งานที่จำเป็นได้ง่าย โดยค่าจริงจะถูกบันทึกผ่าน API ในขั้นถัดไป">
      <template #actions><button class="btn btn-primary" type="button" @click="saveSettings">บันทึกการตั้งค่า</button></template>
    </PageHeader>

    <div class="grid gap-6 lg:grid-cols-[1fr_20rem]">
      <div class="space-y-6">
        <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body gap-6"><div><h2 class="card-title">การเข้าสู่ระบบ</h2><p class="text-sm text-base-content/60">กำหนด policy สำหรับ session โดยไม่ต้องแก้ไฟล์ config</p></div>
          <div class="form-control"><label class="label cursor-pointer justify-start gap-3"><input v-model="sessionMode" class="radio radio-primary" type="radio" value="role" /><span><span class="label-text font-medium">จำกัดตาม role</span><span class="block text-xs text-base-content/60">Admin และผู้เข้าสอบใช้ค่าแยกกัน</span></span></label><label class="label cursor-pointer justify-start gap-3"><input v-model="sessionMode" class="radio radio-primary" type="radio" value="single" /><span><span class="label-text font-medium">หนึ่ง session ต่อคน</span><span class="block text-xs text-base-content/60">เหมาะกับการควบคุมเข้มงวด</span></span></label></div>
          <div><div class="flex justify-between"><label class="label-text font-medium" for="max-sessions">จำนวน session สูงสุดของ Admin</label><span class="badge badge-primary">{{ maxSessions }}</span></div><input id="max-sessions" v-model="maxSessions" class="range range-primary" type="range" min="1" max="10" step="1" /><div class="flex justify-between px-1 text-xs text-base-content/50"><span>1</span><span>10</span></div></div>
          <div><div class="flex justify-between"><label class="label-text font-medium" for="idle-timeout">หมดเวลาเมื่อไม่มีการใช้งาน (นาที)</label><span class="badge badge-primary">{{ idleTimeout }}</span></div><input id="idle-timeout" v-model="idleTimeout" class="range range-primary" type="range" min="5" max="120" step="5" /><div class="flex justify-between px-1 text-xs text-base-content/50"><span>5</span><span>120</span></div></div>
        </div></section>

        <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="card-title">การนำเข้าบุคลากร</h2><p class="text-sm text-base-content/60">ตัวเลือกที่มีผลต่อการตรวจสอบไฟล์ CSV รอบถัดไป</p><label class="label mt-3 cursor-pointer justify-between"><span><span class="label-text font-medium">ตรวจสอบข้อมูลเข้มงวด</span><span class="block text-xs text-base-content/60">หยุดทั้ง batch เมื่อพบข้อมูลผิดรูปแบบ</span></span><input v-model="strictImport" class="toggle toggle-primary" type="checkbox" /></label></div></section>
      </div>

      <aside class="space-y-6"><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="card-title text-base">การแสดงผล</h2><p class="text-sm text-base-content/60">การตั้งค่านี้เป็น client-side UI state</p><ThemeSelector /></div></section><section class="alert alert-info"><span aria-hidden="true">ⓘ</span><div><p class="font-semibold">ปลอดภัยต่อการขยายระบบ</p><p class="text-xs">ค่าตั้งค่าจะถูกตรวจสอบและบันทึกผ่าน API เมื่อ backend endpoint พร้อมใช้งาน</p></div></section></aside>
    </div>
    <AppToast :visible="toastVisible" message="บันทึกค่าในหน้าจอ POC แล้ว" type="success" @dismiss="toastVisible = false" />
  </PageContainer>
</template>
