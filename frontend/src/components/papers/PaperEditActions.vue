<script setup lang="ts">
defineProps<{ canEdit: boolean; canRevise: boolean; revisionNumber: number }>();
defineEmits<{ edit: []; revise: [] }>();
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <button v-if="canEdit" class="btn btn-outline btn-sm" type="button" data-testid="edit-paper" @click="$emit('edit')">แก้ไข Draft</button>
    <button v-if="canRevise" class="btn btn-ghost btn-sm" type="button" data-testid="revise-paper" @click="$emit('revise')">สร้าง Revision {{ revisionNumber + 1 }}</button>
  </div>
</template>
