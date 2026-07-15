<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";

import ThemeSelector from "@/components/settings/ThemeSelector.vue";
import { useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();

onMounted(themeStore.initialize);
</script>

<template>
  <div class="min-h-screen bg-base-200/50">
    <header class="navbar sticky top-0 z-20 border-b border-base-300 bg-base-100/95 px-4 backdrop-blur">
      <div class="mx-auto flex w-full max-w-7xl items-center justify-between gap-4">
        <div class="flex items-center gap-3"><RouterLink class="flex items-center gap-3" to="/"><div class="grid size-10 place-items-center rounded-xl bg-primary font-black text-primary-content">M</div><div><p class="font-bold leading-none">MTExam</p><p class="text-xs text-base-content/50">ระบบบริหารการสอบ</p></div></RouterLink><nav class="hidden gap-1 sm:flex"><RouterLink class="btn btn-ghost btn-sm" active-class="btn-active" to="/">ภาพรวม</RouterLink><RouterLink class="btn btn-ghost btn-sm" active-class="btn-active" to="/exam/pdpa">ทำข้อสอบ</RouterLink><RouterLink class="btn btn-ghost btn-sm" active-class="btn-active" to="/settings">ตั้งค่าระบบ</RouterLink></nav></div>
        <div class="flex items-center gap-2"><span class="hidden text-xs text-base-content/50 sm:inline">โหมดผู้ดูแลระบบ</span>
        <ThemeSelector />
        </div>
      </div>
    </header>
    <RouterView />
  </div>
</template>
