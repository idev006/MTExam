<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  hint: string;
  icon: string;
  tone?: "primary" | "success" | "warning" | "info";
}>();
</script>

<template>
  <div class="card border border-base-300 bg-base-100 shadow-sm">
    <div class="card-body p-5">
      <div class="flex items-start justify-between gap-3">
        <div><p class="text-sm text-base-content/60">{{ label }}</p><p class="mt-2 text-3xl font-bold tracking-tight">{{ value }}</p></div>
        <div class="grid size-11 place-items-center rounded-xl bg-base-200 text-lg" :class="`text-${tone ?? 'primary'}`" aria-hidden="true">{{ icon }}</div>
      </div>
      <p class="mt-2 text-xs text-base-content/60">{{ hint }}</p>
    </div>
  </div>
</template>
