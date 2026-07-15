<script setup lang="ts">
import { onMounted, ref } from "vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { apiGet } from "@/api/client";
interface Event { id: string; event_type: string; subject_type: string; subject_id: string | null; occurred_at: string; metadata: string | null }
const events = ref<Event[]>([]); const error = ref("");
onMounted(async () => { try { events.value = await apiGet<Event[]>("/audit"); } catch (e) { error.value = e instanceof Error ? e.message : "โหลด audit ไม่สำเร็จ"; } });
</script>
<template><PageContainer><PageHeader eyebrow="Super Admin" title="Audit Log" description="ตรวจสอบการเปลี่ยนแปลงที่สำคัญของระบบ" /><div v-if="error" class="alert alert-error">{{ error }}</div><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body overflow-x-auto"><table class="table table-sm"><thead><tr><th>เวลา</th><th>Event</th><th>Subject</th><th>รายละเอียด</th></tr></thead><tbody><tr v-for="event in events" :key="event.id"><td>{{ event.occurred_at }}</td><td><span class="badge badge-primary">{{ event.event_type }}</span></td><td>{{ event.subject_type }} {{ event.subject_id }}</td><td class="max-w-sm truncate">{{ event.metadata }}</td></tr></tbody></table></div></section></PageContainer></template>
