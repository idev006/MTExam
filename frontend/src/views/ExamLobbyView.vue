<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import { apiGet } from "@/api/client";
interface Window { id: string; exam_paper_id: string; status: string; mode: string; duration_minutes: number | null; window_open_at: string | null; window_close_at: string | null }
const windows = ref<Window[]>([]); const error = ref("");
onMounted(async () => { try { windows.value = await apiGet<Window[]>("/exam-windows"); } catch (e) { error.value = e instanceof Error ? e.message : "โหลดรายการสอบไม่สำเร็จ"; } });
</script>
<template><PageContainer><PageHeader eyebrow="Examinee" title="รายการสอบ" description="เลือก Exam Window ที่เปิดให้เข้าสอบ ระบบจะบันทึกคำตอบและสามารถกลับมาทำต่อได้" /><AppAlert v-if="error" type="error">{{ error }}</AppAlert><div class="grid gap-4 md:grid-cols-2"><article v-for="item in windows.filter((window) => window.status === 'open')" :key="item.id" class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><div class="flex items-center justify-between"><h2 class="card-title">Exam Paper</h2><span class="badge badge-success">เปิดสอบ</span></div><p>เวลา {{ item.duration_minutes || 60 }} นาที</p><RouterLink class="btn btn-primary mt-3" :to="`/exam/window/${item.id}`">เริ่ม/ทำต่อ</RouterLink></div></article></div><div v-if="!windows.some((window) => window.status === 'open')" class="alert mt-4">ยังไม่มีรายการสอบที่เปิดอยู่</div></PageContainer></template>
