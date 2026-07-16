<script setup lang="ts">
import type { ReportContext, ReportFilters, ReportOption } from "@/types/reporting";

const props = defineProps<{
  context: ReportContext | null;
  filters: ReportFilters;
  windows: ReportOption[];
}>();
defineEmits<{ apply: []; reset: [] }>();

function subjectChanged() {
  props.filters.exam_paper_id = "";
  props.filters.exam_window_id = "";
}
function paperChanged() { props.filters.exam_window_id = ""; }
</script>

<template>
  <form class="grid gap-4" @submit.prevent="$emit('apply')">
    <label class="form-control"><span class="label-text">รายวิชา</span><select v-model="filters.subject_id" class="select select-bordered w-full" @change="subjectChanged"><option value="">ทั้งหมด</option><option v-for="row in context?.subjects" :key="row.id" :value="row.id">{{ row.label }}</option></select></label>
    <label class="form-control"><span class="label-text">Exam Creation</span><select v-model="filters.exam_paper_id" class="select select-bordered w-full" @change="paperChanged"><option value="">ล่าสุดใน scope</option><option v-for="row in context?.exam_creations" :key="row.id" :value="row.id">{{ row.label }}</option></select></label>
    <label class="form-control"><span class="label-text">Exam Window</span><select v-model="filters.exam_window_id" class="select select-bordered w-full"><option value="">ทุก Window</option><option v-for="row in windows" :key="row.id" :value="row.id">{{ row.label }}</option></select></label>
    <div class="grid grid-cols-2 gap-2"><label class="form-control"><span class="label-text">ตั้งแต่</span><input v-model="filters.date_from" class="input input-bordered" type="date" /></label><label class="form-control"><span class="label-text">ถึง</span><input v-model="filters.date_to" class="input input-bordered" type="date" /></label></div>
    <label v-if="context?.role !== 'examinee'" class="form-control"><span class="label-text">หน่วยงาน</span><select v-model="filters.org_unit_id" class="select select-bordered w-full"><option value="">ทุกหน่วยใน scope</option><option v-for="row in context?.organizations" :key="row.id" :value="row.id">{{ row.label }}</option></select></label>
    <div class="grid grid-cols-2 gap-2"><button class="btn btn-primary" type="submit">ใช้ตัวกรอง</button><button class="btn btn-ghost" type="button" @click="$emit('reset')">รีเซ็ต</button></div>
  </form>
</template>
