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
const canViewReports = computed(() => user.value?.role === "super_admin" || user.value?.role === "viewer");
const canAuthor = computed(() => user.value?.role === "super_admin" || user.value?.role === "exam_author");
const isSuperAdmin = computed(() => user.value?.role === "super_admin");
const roleLabel = computed(() => user.value?.role ?? "ผู้เยี่ยมชม");
const showLogoutModal = ref(false);
const logoutError = ref("");
const isLoggingOut = ref(false);
const mobileMenuOpen = ref(false);

onMounted(themeStore.initialize);

async function confirmLogout() {
  isLoggingOut.value = true;
  logoutError.value = "";
  try {
    await logout();
    showLogoutModal.value = false;
    mobileMenuOpen.value = false;
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
    <header v-if="!isLoginPage" class="sticky top-0 z-30 border-b border-base-300 bg-base-100/95 backdrop-blur">
      <div class="navbar mx-auto min-h-16 w-full max-w-7xl gap-2 px-3 sm:px-5">
        <div class="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <button class="btn btn-square btn-ghost lg:hidden" type="button" aria-label="เปิดเมนู" @click="mobileMenuOpen = !mobileMenuOpen">
            <svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
          <RouterLink class="flex min-w-0 items-center gap-2 sm:gap-3" to="/" @click="mobileMenuOpen = false">
            <div class="grid size-9 shrink-0 place-items-center rounded-xl bg-primary font-black text-primary-content sm:size-10">M</div>
            <div class="min-w-0"><p class="truncate font-bold leading-none">MTExam</p><p class="hidden truncate text-xs text-base-content/50 sm:block">ระบบบริหารการสอบ</p></div>
          </RouterLink>
          <nav class="hidden items-center gap-1 lg:flex">
            <RouterLink class="btn btn-ghost btn-sm" active-class="btn-active" to="/">ภาพรวม</RouterLink>
            <RouterLink v-if="canTakeExam" class="btn btn-ghost btn-sm" active-class="btn-active" to="/exam">ทำข้อสอบ</RouterLink>
            <RouterLink v-if="canAuthor" class="btn btn-ghost btn-sm" active-class="btn-active" to="/authoring">คลังข้อสอบ</RouterLink>
            <RouterLink v-if="canAuthor" class="btn btn-ghost btn-sm" active-class="btn-active" to="/papers">Exam Paper</RouterLink>
            <RouterLink v-if="canViewReports" class="btn btn-ghost btn-sm" active-class="btn-active" to="/reports">รายงาน</RouterLink>
            <RouterLink v-if="canViewReports" class="btn btn-ghost btn-sm" active-class="btn-active" to="/audit">Audit</RouterLink>
            <RouterLink v-if="isSuperAdmin" class="btn btn-ghost btn-sm" active-class="btn-active" to="/admin/users">ผู้ใช้</RouterLink>
            <RouterLink v-if="canViewSettings" class="btn btn-ghost btn-sm" active-class="btn-active" to="/settings">ตั้งค่าระบบ</RouterLink>
          </nav>
        </div>
        <div class="flex shrink-0 items-center gap-2 sm:gap-3">
          <div v-if="user" class="hidden text-right md:block"><p class="text-xs text-base-content/60">ยินดีต้อนรับ คุณ {{ user.full_name }}</p><span class="badge badge-ghost whitespace-nowrap text-xs">{{ roleLabel }}</span></div>
          <ThemeSelector />
          <RouterLink v-if="!user" class="btn btn-primary btn-sm" to="/login">เข้าสู่ระบบ</RouterLink>
          <button v-else class="btn btn-ghost btn-sm hidden sm:inline-flex" type="button" @click="showLogoutModal = true">ออกจากระบบ</button>
        </div>
      </div>
      <div v-if="mobileMenuOpen" class="border-t border-base-300 bg-base-100 p-3 shadow-lg lg:hidden">
        <div v-if="user" class="mb-2 rounded-box bg-base-200 p-3"><p class="text-sm">ยินดีต้อนรับ คุณ {{ user.full_name }}</p><span class="badge badge-primary mt-1 whitespace-nowrap">{{ roleLabel }}</span></div>
        <nav class="grid gap-1">
          <RouterLink class="btn btn-ghost justify-start" to="/" @click="mobileMenuOpen = false">ภาพรวม</RouterLink>
          <RouterLink v-if="canTakeExam" class="btn btn-ghost justify-start" to="/exam" @click="mobileMenuOpen = false">ทำข้อสอบ</RouterLink>
          <RouterLink v-if="canAuthor" class="btn btn-ghost justify-start" to="/authoring" @click="mobileMenuOpen = false">คลังข้อสอบ</RouterLink>
          <RouterLink v-if="canAuthor" class="btn btn-ghost justify-start" to="/papers" @click="mobileMenuOpen = false">Exam Paper</RouterLink>
          <RouterLink v-if="canViewReports" class="btn btn-ghost justify-start" to="/reports" @click="mobileMenuOpen = false">รายงาน</RouterLink>
          <RouterLink v-if="canViewReports" class="btn btn-ghost justify-start" to="/audit" @click="mobileMenuOpen = false">Audit</RouterLink>
          <RouterLink v-if="isSuperAdmin" class="btn btn-ghost justify-start" to="/admin/users" @click="mobileMenuOpen = false">ผู้ใช้</RouterLink>
          <RouterLink v-if="canViewSettings" class="btn btn-ghost justify-start" to="/settings" @click="mobileMenuOpen = false">ตั้งค่าระบบ</RouterLink>
          <button v-if="user" class="btn btn-outline mt-2 justify-start sm:hidden" type="button" @click="showLogoutModal = true">ออกจากระบบ</button>
        </nav>
      </div>
    </header>
    <header v-else class="flex items-center justify-between border-b border-base-300 bg-base-100/80 px-4 py-3 sm:px-5 sm:py-4 backdrop-blur"><RouterLink class="flex items-center gap-3" to="/"><div class="grid size-9 place-items-center rounded-xl bg-primary font-black text-primary-content sm:size-10">M</div><div><p class="font-bold leading-none">MTExam</p><p class="hidden text-xs text-base-content/50 sm:block">ระบบบริหารการสอบ</p></div></RouterLink><ThemeSelector /></header>
    <RouterView />
    <div v-if="logoutError" class="toast toast-end toast-bottom z-50"><div class="alert alert-error"><span>{{ logoutError }}</span><button class="btn btn-ghost btn-xs" type="button" @click="logoutError = ''">ปิด</button></div></div>
    <ConfirmModal :open="showLogoutModal" title="ยืนยันการออกจากระบบ" message="คุณต้องการออกจากระบบใช่หรือไม่ ระบบจะพาคุณกลับไปหน้าเข้าสู่ระบบ" confirm-label="ออกจากระบบ" cancel-label="ยกเลิก" :busy="isLoggingOut" @confirm="confirmLogout" @cancel="showLogoutModal = false" />
  </div>
</template>
