import { computed, ref } from "vue";

import { apiGet } from "@/api/client";
import type { PracticeBank } from "@/types/practiceExam";

export function usePracticeExam() {
  const bank = ref<PracticeBank | null>(null);
  const currentIndex = ref(0);
  const selectedIndex = ref<number | null>(null);
  const submittedIndex = ref<number | null>(null);
  const score = ref(0);
  const isLoading = ref(false);
  const errorMessage = ref("");

  const currentQuestion = computed(() => bank.value?.questions[currentIndex.value] ?? null);
  const isSubmitted = computed(() => submittedIndex.value !== null);
  const progress = computed(() => (bank.value ? Math.round(((currentIndex.value + 1) / bank.value.questions.length) * 100) : 0));

  async function load() {
    isLoading.value = true;
    errorMessage.value = "";
    try {
      bank.value = await apiGet<PracticeBank>("/practice/banks/pdpa-50");
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "โหลดชุดข้อสอบไม่สำเร็จ";
    } finally {
      isLoading.value = false;
    }
  }

  function submitAnswer() {
    if (selectedIndex.value === null || submittedIndex.value !== null || !currentQuestion.value) return;
    submittedIndex.value = selectedIndex.value;
    if (selectedIndex.value === currentQuestion.value.correct_index) score.value += 1;
  }

  function nextQuestion() {
    if (!bank.value || currentIndex.value >= bank.value.questions.length - 1) return;
    currentIndex.value += 1;
    selectedIndex.value = null;
    submittedIndex.value = null;
  }

  return { bank, currentIndex, currentQuestion, selectedIndex, submittedIndex, score, isLoading, errorMessage, isSubmitted, progress, load, submitAnswer, nextQuestion };
}
