import { computed, ref } from "vue";

import { apiGet } from "@/api/client";
import type { PracticeBank } from "@/types/practiceExam";

export function usePracticeExam() {
  const bank = ref<PracticeBank | null>(null);
  const currentIndex = ref(0);
  const selectedIndex = ref<number | null>(null);
  const answers = ref<Record<number, number>>({});
  const isFinalSubmitted = ref(false);
  const score = ref(0);
  const isLoading = ref(false);
  const errorMessage = ref("");

  const currentQuestion = computed(() => bank.value?.questions[currentIndex.value] ?? null);
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

  function saveCurrentAnswer() {
    if (selectedIndex.value === null) return false;
    answers.value[currentIndex.value] = selectedIndex.value;
    return true;
  }

  function nextQuestion() {
    if (!bank.value || !saveCurrentAnswer() || currentIndex.value >= bank.value.questions.length - 1) return;
    currentIndex.value += 1;
    selectedIndex.value = answers.value[currentIndex.value] ?? null;
  }

  function finishExam() {
    if (!bank.value || !saveCurrentAnswer()) return;
    score.value = bank.value.questions.reduce(
      (total, question, index) => total + (answers.value[index] === question.correct_index ? 1 : 0),
      0,
    );
    isFinalSubmitted.value = true;
  }

  return { bank, currentIndex, currentQuestion, selectedIndex, answers, score, isLoading, errorMessage, isFinalSubmitted, progress, load, nextQuestion, finishExam };
}
