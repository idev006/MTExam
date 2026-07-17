<script setup lang="ts">
export type WindowStatus = "scheduled" | "open" | "suspended" | "closed" | "cancelled";

defineProps<{ status: WindowStatus }>();
defineEmits<{ request: [status: Exclude<WindowStatus, "scheduled">] }>();
</script>

<template>
  <div class="flex flex-wrap justify-end gap-2" aria-label="จัดการสถานะรอบสอบ">
    <button v-if="status === 'scheduled' || status === 'suspended'" class="btn btn-primary btn-sm" type="button" data-testid="open-window" @click="$emit('request', 'open')">เปิดรอบสอบ</button>
    <button v-if="status === 'open'" class="btn btn-warning btn-sm" type="button" data-testid="suspend-window" @click="$emit('request', 'suspended')">ระงับชั่วคราว</button>
    <button v-if="status === 'open' || status === 'suspended'" class="btn btn-error btn-outline btn-sm" type="button" data-testid="close-window" @click="$emit('request', 'closed')">ปิดรอบสอบ</button>
    <button v-if="status === 'scheduled' || status === 'suspended'" class="btn btn-ghost btn-sm" type="button" data-testid="cancel-window" @click="$emit('request', 'cancelled')">ยกเลิกรอบ</button>
    <span v-if="status === 'closed' || status === 'cancelled'" class="text-sm text-base-content/50">รอบสอบสิ้นสุดแล้ว</span>
  </div>
</template>
