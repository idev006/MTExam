<script setup lang="ts">
import { onMounted } from "vue";
import { RouterView } from "vue-router";

import ThemeSelector from "@/components/settings/ThemeSelector.vue";
import { useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();

onMounted(themeStore.initialize);
</script>

<template>
  <div class="min-h-screen bg-base-200/50">
    <header class="navbar sticky top-0 z-20 border-b border-base-300 bg-base-100/95 px-4 backdrop-blur">
      <div class="mx-auto flex w-full max-w-7xl items-center justify-between gap-4">
        <div class="flex items-center gap-3"><div class="grid size-10 place-items-center rounded-xl bg-primary font-black text-primary-content">M</div><div><p class="font-bold leading-none">MTExam</p><p class="text-xs text-base-content/50">ระบบบริหารการสอบ</p></div></div>
        <div class="flex items-center gap-2"><span class="hidden text-xs text-base-content/50 sm:inline">โหมดผู้ดูแลระบบ</span>
        <ThemeSelector />
        </div>
      </div>
    </header>
    <RouterView />
  </div>
</template>
