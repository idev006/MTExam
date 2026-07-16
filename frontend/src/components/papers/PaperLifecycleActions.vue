<script setup lang="ts">
export type PaperLifecycleStatus = "draft" | "published" | "archived";

defineProps<{ status: PaperLifecycleStatus }>();

defineEmits<{
  request: [status: PaperLifecycleStatus];
}>();
</script>

<template>
  <div class="flex flex-wrap justify-end gap-2" aria-label="จัดการสถานะ Exam Creation">
    <button
      v-if="status !== 'published'"
      class="btn btn-primary btn-sm"
      type="button"
      data-testid="publish-paper"
      @click="$emit('request', 'published')"
    >
      เปิดใช้งาน
    </button>
    <button
      v-if="status === 'published'"
      class="btn btn-warning btn-sm"
      type="button"
      data-testid="archive-paper"
      @click="$emit('request', 'archived')"
    >
      ปิดใช้งาน
    </button>
    <button
      v-if="status !== 'draft'"
      class="btn btn-ghost btn-sm"
      type="button"
      data-testid="draft-paper"
      @click="$emit('request', 'draft')"
    >
      กลับเป็น Draft
    </button>
  </div>
</template>
