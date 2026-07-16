<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import { apiRequest } from "@/api/client";
interface Question { id: string; content: string; choices: { id: string; content: string }[] }
interface Session { id: string; status: string; ends_at: string; score: number | null; answers: Record<string, string>; questions: Question[] }
const route = useRoute(); const session = ref<Session | null>(null); const error = ref(""); const saving = ref(false); const remaining = ref(0);
const answered = computed(() => Object.keys(session.value?.answers || {}).length);
function updateClock() { if (session.value) remaining.value = Math.max(0, Math.floor((new Date(session.value.ends_at).getTime() - Date.now()) / 1000)); }
async function start() { try { session.value = await apiRequest<Session>(`/exam-sessions/windows/${route.params.windowId}/start`, "POST"); updateClock(); } catch (e) { error.value = e instanceof Error ? e.message : "เริ่มสอบไม่สำเร็จ"; } }
async function answer(questionId: string, choiceId: string) { if (!session.value) return; saving.value = true; try { session.value = await apiRequest<Session>(`/exam-sessions/${session.value.id}/answers`, "PUT", { variant_question_id: questionId, selected_choice_id: choiceId }); } catch (e) { error.value = e instanceof Error ? e.message : "บันทึกคำตอบไม่สำเร็จ"; } finally { saving.value = false; } }
async function submit() { if (!session.value) return; try { session.value = await apiRequest<Session>(`/exam-sessions/${session.value.id}/submit`, "POST"); } catch (e) { error.value = e instanceof Error ? e.message : "ส่งข้อสอบไม่สำเร็จ"; } }
onMounted(async () => { await start(); window.setInterval(updateClock, 1000); });
</script>
<template><PageContainer><PageHeader eyebrow="Examinee" title="ทำข้อสอบ" description="คำตอบถูกบันทึกลงระบบทุกครั้งที่เลือก และใช้เวลาจาก server" /><AppAlert v-if="error" type="error">{{ error }}</AppAlert><div v-if="session" class="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-box border border-base-300 bg-base-100 p-4"><span>ทำแล้ว {{ answered }} / {{ session.questions.length }} ข้อ</span><span class="badge badge-warning">เหลือ {{ Math.floor(remaining / 60) }}:{{ String(remaining % 60).padStart(2, '0') }}</span><button v-if="session.status === 'in_progress'" class="btn btn-primary" type="button" @click="submit">ส่งข้อสอบ</button><span v-else class="badge badge-success">คะแนน {{ session.score }}</span></div><div v-if="session" class="space-y-4"><article v-for="(question, index) in session.questions" :key="question.id" class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="font-semibold">{{ index + 1 }}. {{ question.content }}</h2><label v-for="choice in question.choices" :key="choice.id" class="label cursor-pointer justify-start gap-3"><input class="radio radio-primary" type="radio" :name="question.id" :checked="session.answers[question.id] === choice.id" :disabled="session.status !== 'in_progress' || saving" @change="answer(question.id, choice.id)" /><span>{{ choice.content }}</span></label></div></article></div></PageContainer></template>
