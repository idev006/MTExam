<script setup lang="ts">
import { DAISYUI_THEMES, type DaisyTheme, useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();

function selectTheme(event: Event): void {
  themeStore.setTheme((event.target as HTMLSelectElement).value as DaisyTheme);
}

function themeLabel(theme: DaisyTheme): string {
  return theme.replace(/([a-z])([A-Z])/g, "$1 $2");
}
</script>

<template>
  <label class="form-control w-full max-w-xs">
    <span class="label-text text-xs font-medium">ธีม</span>
    <select
      class="select select-bordered select-sm"
      :value="themeStore.theme"
      aria-label="เลือกธีม"
      @change="selectTheme"
    >
      <option v-for="theme in DAISYUI_THEMES" :key="theme" :value="theme">
        {{ themeLabel(theme) }}
      </option>
    </select>
  </label>
</template>
