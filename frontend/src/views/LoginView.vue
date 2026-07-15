<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import AppAlert from "@/components/feedback/AppAlert.vue";
import { useAuth } from "@/stores/auth";

const router = useRouter();
const { login } = useAuth();
const username = ref("");
const password = ref("");
const error = ref("");
const isLoading = ref(false);

async function submit() {
  error.value = "";
  isLoading.value = true;
  try {
    await login(username.value, password.value);
    await router.push((router.currentRoute.value.query.redirect as string) || "/");
  } catch {
    error.value = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <main class="auth-shell min-h-[calc(100vh-5rem)] px-4 py-8 sm:px-6 lg:px-8">
    <div class="mx-auto grid w-full max-w-5xl overflow-hidden rounded-3xl border border-base-300 bg-base-100 shadow-xl lg:grid-cols-[1fr_1.08fr]">
      <section class="hidden bg-primary p-10 text-primary-content lg:flex lg:flex-col lg:justify-between">
        <div>
          <div class="mb-10 flex items-center gap-3"><div class="grid size-12 place-items-center rounded-2xl bg-primary-content text-xl font-bold text-primary">M</div><div><p class="text-xl font-bold">MTExam</p><p class="text-sm opacity-75">ระบบบริหารการสอบ</p></div></div>
          <p class="max-w-sm text-3xl font-bold leading-tight">เข้าสู่ระบบเพื่อเริ่มทำข้อสอบอย่างมั่นใจ</p>
          <p class="mt-4 max-w-sm text-sm leading-6 opacity-80">ระบบจะบันทึกคำตอบอย่างต่อเนื่อง และช่วยให้คุณกลับมาทำข้อสอบต่อได้เมื่อเกิดเหตุขัดข้อง</p>
        </div>
        <p class="text-xs opacity-60">ปลอดภัย · กู้คืนได้ · ใช้งานง่าย</p>
      </section>

      <section class="p-6 sm:p-10 lg:p-12">
        <div class="mb-8 lg:hidden"><div class="flex items-center gap-3"><div class="grid size-11 place-items-center rounded-2xl bg-primary text-lg font-bold text-primary-content">M</div><div><p class="text-lg font-bold">MTExam</p><p class="text-xs text-base-content/60">ระบบบริหารการสอบ</p></div></div></div>
        <div class="mb-8"><p class="text-sm font-semibold text-primary">ยินดีต้อนรับ</p><h1 class="mt-2 text-3xl font-bold tracking-tight">เข้าสู่ระบบ</h1><p class="mt-2 text-sm leading-6 text-base-content/60">กรอกข้อมูลเพื่อเข้าสู่ระบบและทำข้อสอบต่อจากจุดเดิม</p></div>
        <AppAlert v-if="error" type="error" class="mb-5">{{ error }}</AppAlert>
        <form class="space-y-5" @submit.prevent="submit">
          <label class="form-control w-full"><span class="label pb-2"><span class="label-text font-semibold">ชื่อผู้ใช้</span></span><input v-model="username" class="input input-bordered input-lg w-full" autocomplete="username" placeholder="กรอกชื่อผู้ใช้" required /></label>
          <label class="form-control w-full"><span class="label pb-2"><span class="label-text font-semibold">รหัสผ่าน</span></span><input v-model="password" class="input input-bordered input-lg w-full" type="password" autocomplete="current-password" placeholder="กรอกรหัสผ่าน" required /></label>
          <button class="btn btn-primary btn-lg w-full" :disabled="isLoading" type="submit"><span v-if="isLoading" class="loading loading-spinner loading-sm"></span>{{ isLoading ? "กำลังตรวจสอบ..." : "เข้าสู่ระบบ" }}</button>
        </form>
        <div class="divider my-7 text-xs text-base-content/40">การเข้าสู่ระบบที่ปลอดภัย</div>
        <p class="text-center text-xs leading-5 text-base-content/50">ระบบจะใช้ session ที่ปลอดภัย และไม่เปิดเผยคะแนนหรือเฉลยก่อนส่งข้อสอบ</p>
      </section>
    </div>
  </main>
</template>
