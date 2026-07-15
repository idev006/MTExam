<script setup lang="ts">
import { onMounted } from "vue";
import { RouterView } from "vue-router";

import ThemeSelector from "@/components/settings/ThemeSelector.vue";
import { useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();

onMounted(themeStore.initialize);
</script>

<template>
  <div class="min-h-screen">
    <header class="navbar border-b border-base-300 bg-base-100 px-4">
      <div class="mx-auto flex w-full max-w-6xl items-end justify-between gap-4">
        <span class="text-xl font-bold">MTExam</span>
        <ThemeSelector />
      </div>
    </header>
    <RouterView />
  </div>
</template>
