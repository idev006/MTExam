<script setup lang="ts">
import { computed } from "vue";

type ToastType = "info" | "success" | "warning" | "error";

const props = withDefaults(
  defineProps<{
    message: string;
    type?: ToastType;
    visible?: boolean;
  }>(),
  { type: "info", visible: true },
);

const emit = defineEmits<{
  dismiss: [];
}>();

const toastClass = computed(() => `alert-${props.type}`);
</script>

<template>
  <div v-if="visible" class="toast toast-end toast-bottom z-50">
    <div class="alert shadow-lg" :class="toastClass" role="status" aria-live="polite">
      <span>{{ message }}</span>
      <button class="btn btn-ghost btn-xs" type="button" aria-label="ปิดข้อความ" @click="emit('dismiss')">
        ปิด
      </button>
    </div>
  </div>
</template>
