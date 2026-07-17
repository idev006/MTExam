<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import { apiGet, apiRequest } from "@/api/client";
import ExamSubmitPanel from "@/components/exam/ExamSubmitPanel.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";

interface Question {
  id: string;
  content: string;
  explanation?: string | null;
  choices: { id: string; content: string }[];
}
interface ExamSession {
  id: string;
  status: "in_progress" | "submitted" | "timed_out" | "force_closed";
  ends_at: string;
  score: number | null;
  maximum_score: number | null;
  percentage: number | null;
  passing_percentage: number | null;
  passed: boolean | null;
  result_visible: boolean;
  answers: Record<string, string>;
  questions: Question[];
}

const route = useRoute();
const session = ref<ExamSession | null>(null);
const error = ref("");
const saving = ref(false);
const submitting = ref(false);
const remaining = ref(0);
let timerId: number | undefined;
let timeoutRefreshed = false;

const answered = computed(() => Object.keys(session.value?.answers ?? {}).length);
const terminalLabel = computed(() => {
  if (session.value?.status === "timed_out") return "หมดเวลาและส่งคำตอบอัตโนมัติแล้ว";
  if (session.value?.status === "force_closed") return "เจ้าหน้าที่ปิดการสอบแล้ว";
  return "ส่งข้อสอบแล้ว";
});

async function updateClock() {
  if (!session.value || session.value.status !== "in_progress") return;
  remaining.value = Math.max(
    0,
    Math.floor((new Date(session.value.ends_at).getTime() - Date.now()) / 1000),
  );
  if (remaining.value === 0 && !timeoutRefreshed) {
    timeoutRefreshed = true;
    try {
      session.value = await apiGet<ExamSession>(`/exam-sessions/${session.value.id}`);
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : "ตรวจสอบสถานะหมดเวลาไม่สำเร็จ";
    }
  }
}

async function start() {
  try {
    session.value = await apiRequest<ExamSession>(
      `/exam-sessions/windows/${route.params.windowId}/start`,
      "POST",
    );
    await updateClock();
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "เริ่มสอบไม่สำเร็จ";
  }
}

async function answer(questionId: string, choiceId: string) {
  if (!session.value) return;
  saving.value = true;
  error.value = "";
  try {
    session.value = await apiRequest<ExamSession>(
      `/exam-sessions/${session.value.id}/answers`,
      "PUT",
      { variant_question_id: questionId, selected_choice_id: choiceId },
    );
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "บันทึกคำตอบไม่สำเร็จ";
  } finally {
    saving.value = false;
  }
}

async function submit() {
  if (!session.value) return;
  submitting.value = true;
  error.value = "";
  try {
    session.value = await apiRequest<ExamSession>(
      `/exam-sessions/${session.value.id}/submit`,
      "POST",
    );
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "ส่งข้อสอบไม่สำเร็จ";
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  await start();
  timerId = window.setInterval(updateClock, 1000);
});
onUnmounted(() => window.clearInterval(timerId));
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="Examinee" title="ทำข้อสอบ" description="ระบบบันทึกทุกคำตอบและใช้เวลาจาก server เป็นหลัก" />
    <AppAlert v-if="error" type="error">{{ error }}</AppAlert>

    <section v-if="session" class="mb-4 rounded-box border border-base-300 bg-base-100 p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <span>ทำแล้ว {{ answered }} / {{ session.questions.length }} ข้อ</span>
        <span v-if="session.status === 'in_progress'" class="badge badge-warning">
          เหลือ {{ Math.floor(remaining / 60) }}:{{ String(remaining % 60).padStart(2, "0") }}
        </span>
        <ExamSubmitPanel
          :status="session.status"
          :answered="answered"
          :total="session.questions.length"
          :remaining="remaining"
          :submitting="submitting"
          @submit="submit"
        />
      </div>
      <div v-if="session.status !== 'in_progress'" class="mt-4">
        <AppAlert type="success">{{ terminalLabel }}</AppAlert>
        <div v-if="session.result_visible" class="stats stats-vertical w-full border border-base-300 sm:stats-horizontal">
          <div class="stat"><div class="stat-title">คะแนน</div><div class="stat-value text-2xl">{{ session.score }} / {{ session.maximum_score }}</div></div>
          <div class="stat"><div class="stat-title">ร้อยละ</div><div class="stat-value text-2xl">{{ session.percentage }}%</div></div>
          <div class="stat"><div class="stat-title">ผลสอบ</div><div class="stat-value text-2xl" :class="session.passed ? 'text-success' : 'text-error'">{{ session.passed ? "ผ่าน" : "ไม่ผ่าน" }}</div><div class="stat-desc">เกณฑ์ {{ session.passing_percentage }}%</div></div>
        </div>
        <AppAlert v-else type="info">รอบสอบนี้ยังไม่เปิดเผยคะแนนและผลสอบ โปรดตรวจสอบอีกครั้งตามประกาศของผู้จัดสอบ</AppAlert>
      </div>
    </section>

    <div v-if="session" class="space-y-4">
      <article v-for="(question, index) in session.questions" :key="question.id" class="card border border-base-300 bg-base-100 shadow-sm">
        <div class="card-body">
          <h2 class="font-semibold">{{ index + 1 }}. {{ question.content }}</h2>
          <label v-for="choice in question.choices" :key="choice.id" class="label cursor-pointer justify-start gap-3">
            <input class="radio radio-primary" type="radio" :name="question.id" :checked="session.answers[question.id] === choice.id" :disabled="session.status !== 'in_progress' || saving" @change="answer(question.id, choice.id)" />
            <span>{{ choice.content }}</span>
          </label>
          <p v-if="question.explanation" class="rounded-box bg-base-200 p-3 text-sm"><strong>คำอธิบาย:</strong> {{ question.explanation }}</p>
        </div>
      </article>
    </div>
  </PageContainer>
</template>
