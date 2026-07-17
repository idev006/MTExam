<script setup lang="ts">
import { computed, ref } from "vue";
import ConfirmModal from "@/components/feedback/ConfirmModal.vue";

const props = defineProps<{
  status: string;
  answered: number;
  total: number;
  remaining: number;
  submitting?: boolean;
}>();

const emit = defineEmits<{ submit: [] }>();
const confirmOpen = ref(false);
const unanswered = computed(() => Math.max(0, props.total - props.answered));
const confirmation = computed(() =>
  unanswered.value
    ? `ยังไม่ได้ตอบ ${unanswered.value} ข้อ เมื่อยืนยันแล้วจะกลับมาแก้ไขคำตอบไม่ได้`
    : "ตอบครบทุกข้อแล้ว เมื่อยืนยันจะไม่สามารถกลับมาแก้ไขคำตอบได้",
);

function confirmSubmit() {
  confirmOpen.value = false;
  emit("submit");
}
</script>

<template>
  <button
    v-if="status === 'in_progress'"
    data-testid="request-submit"
    class="btn btn-primary"
    type="button"
    :disabled="submitting"
    @click="confirmOpen = true"
  >
    <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
    ส่งข้อสอบ
  </button>
  <ConfirmModal
    :open="confirmOpen"
    title="ยืนยันส่งข้อสอบ"
    :message="confirmation"
    confirm-label="ยืนยันส่งข้อสอบ"
    cancel-label="กลับไปตรวจคำตอบ"
    :busy="submitting"
    @confirm="confirmSubmit"
    @cancel="confirmOpen = false"
  />
</template>
