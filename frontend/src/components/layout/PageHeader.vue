<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
  eyebrow?: string;
}>();
</script>

<template>
  <header class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <div v-if="eyebrow" class="badge badge-primary badge-outline mb-2">{{ eyebrow }}</div>
      <h1 class="text-3xl font-bold tracking-tight">{{ title }}</h1>
      <p v-if="description" class="mt-2 max-w-3xl text-base-content/70">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="shrink-0">
      <slot name="actions" />
    </div>
  </header>
</template>
