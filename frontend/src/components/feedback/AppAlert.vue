<script setup lang="ts">
import { computed } from "vue";

type AlertType = "info" | "success" | "warning" | "error";

const props = withDefaults(
  defineProps<{
    type?: AlertType;
  }>(),
  { type: "info" },
);

const alertClass = computed(() => `alert-${props.type}`);
</script>

<template>
  <div class="alert" :class="alertClass" role="status" aria-live="polite">
    <slot />
  </div>
</template>
