<script setup lang="ts">
withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    busy?: boolean;
    confirmDisabled?: boolean;
  }>(),
  { confirmLabel: "ยืนยัน", cancelLabel: "ยกเลิก" },
);

defineEmits<{
  confirm: [];
  cancel: [];
}>();
</script>

<template>
  <dialog class="modal" :class="{ 'modal-open': open }" aria-labelledby="confirm-title">
    <div class="modal-box">
      <h2 id="confirm-title" class="text-lg font-bold">{{ title }}</h2>
      <p class="py-4 text-base-content/70">{{ message }}</p>
      <slot></slot>
      <div class="modal-action">
        <button class="btn btn-ghost" type="button" @click="$emit('cancel')">
          {{ cancelLabel }}
        </button>
        <button class="btn btn-primary" type="button" :disabled="busy || confirmDisabled" @click="$emit('confirm')">
          <span v-if="busy" class="loading loading-spinner loading-sm"></span>
          {{ confirmLabel }}
        </button>
      </div>
    </div>
    <form class="modal-backdrop" method="dialog">
      <button type="button" aria-label="ปิดหน้าต่าง" @click="$emit('cancel')">ปิด</button>
    </form>
  </dialog>
</template>
