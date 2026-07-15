<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";

import ConfirmModal from "@/components/feedback/ConfirmModal.vue";
import ThemeSelector from "@/components/settings/ThemeSelector.vue";
import { useAuth } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();
const { user, logout } = useAuth();
const route = useRoute();
const router = useRouter();
const isLoginPage = computed(() => route.name === "login");
const canTakeExam = computed(() => user.value?.role === "examinee" || user.value?.role === "super_admin");
const canViewSettings = computed(() => user.value?.role === "super_admin");
const showLogoutModal = ref(false);
const logoutError = ref("");
const isLoggingOut = ref(false);

onMounted(themeStore.initialize);

async function confirmLogout() {
  isLoggingOut.value = true;
  logoutError.value = "";
  try {
    await logout();
    showLogoutModal.value = false;
    await router.replace({ name: "login" });
  } catch {
    logoutError.value = "ออกจากระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง";
  } finally {
    isLoggingOut.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-base-200/50">
    <header v-if="!isLoginPage" class="navbar sticky top-0 z-20 border-b border-base-300 bg-base-100/95 px-4 backdrop-blur">
      <div class="mx-auto flex w-full max-w-7xl items-center justify-between gap-4">
        <div class="flex items-center gap-3"><RouterLink class="flex items-center gap-3" to="/"><div class="grid size-10 place-items-center rounded-xl bg-primary font-black text-primary-content">M</div><div><p class="font-bold leading-none">MTExam</p><p class="text-xs text-base-content/50">ระบบบริหารการสอบ</p></div></RouterLink><nav class="hidden gap-1 sm:flex"><RouterLink class="btn btn-ghost btn-sm" active-class="btn-active" to="/">ภาพรวม</RouterLink><RouterLink v-if="canTakeExam" class="btn btn-ghost btn-sm" active-class="btn-active" to="/exam/pdpa">ทำข้อสอบ</RouterLink><RouterLink v-if="canViewSettings" class="btn btn-ghost btn-sm" active-class="btn-active" to="/settings">ตั้งค่าระบบ</RouterLink></nav></div>
        <div class="flex items-center gap-2"><ThemeSelector /><RouterLink v-if="!user" class="btn btn-primary btn-sm" to="/login">เข้าสู่ระบบ</RouterLink><div v-else class="flex items-center gap-2"><span class="hidden text-xs sm:inline">{{ user.full_name }}</span><button class="btn btn-ghost btn-sm" type="button" @click="showLogoutModal = true">ออกจากระบบ</button></div></div>
      </div>
    </header>
    <header v-else class="flex items-center justify-between border-b border-base-300 bg-base-100/80 px-5 py-4 backdrop-blur"><RouterLink class="flex items-center gap-3" to="/"><div class="grid size-10 place-items-center rounded-xl bg-primary font-black text-primary-content">M</div><div><p class="font-bold leading-none">MTExam</p><p class="text-xs text-base-content/50">ระบบบริหารการสอบ</p></div></RouterLink><ThemeSelector /></header>
    <RouterView />
    <div v-if="logoutError" class="toast toast-end toast-bottom z-50"><div class="alert alert-error"><span>{{ logoutError }}</span><button class="btn btn-ghost btn-xs" type="button" @click="logoutError = ''">ปิด</button></div></div>
    <ConfirmModal :open="showLogoutModal" title="ยืนยันการออกจากระบบ" message="คุณต้องการออกจากระบบใช่หรือไม่ ระบบจะพาคุณกลับไปหน้าเข้าสู่ระบบ" confirm-label="ออกจากระบบ" cancel-label="ยกเลิก" :busy="isLoggingOut" @confirm="confirmLogout" @cancel="showLogoutModal = false" />
  </div>
</template>
