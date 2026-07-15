import { computed, ref } from "vue";

import { apiGet } from "@/api/client";
import { useExamSettings } from "@/stores/examSettings";
import type { PracticeBank } from "@/types/practiceExam";

export function usePracticeExam() {
  const bank = ref<PracticeBank | null>(null);
  const currentPage = ref(1);
  const answers = ref<Record<number, number>>({});
  const isFinalSubmitted = ref(false);
  const score = ref(0);
  const isLoading = ref(false);
  const errorMessage = ref("");
  const { pageSize } = useExamSettings();
  const totalPages = computed(() => bank.value ? Math.ceil(bank.value.questions.length / pageSize.value) : 0);
  const pageQuestions = computed(() => bank.value?.questions.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value) ?? []);
  const progress = computed(() => totalPages.value ? Math.round((currentPage.value / totalPages.value) * 100) : 0);
  const answeredCount = computed(() => Object.keys(answers.value).length);

  async function load() {
    isLoading.value = true;
    errorMessage.value = "";
    try { bank.value = await apiGet<PracticeBank>("/practice/banks/pdpa-50"); }
    catch (error) { errorMessage.value = error instanceof Error ? error.message : "โหลดชุดข้อสอบไม่สำเร็จ"; }
    finally { isLoading.value = false; }
  }
  function setAnswer(questionIndex: number, choiceIndex: number) { answers.value[questionIndex] = choiceIndex; }
  function goToPage(page: number) { if (page >= 1 && page <= totalPages.value) currentPage.value = page; }
  function finishExam() {
    if (!bank.value || answeredCount.value !== bank.value.questions.length) return;
    score.value = bank.value.questions.reduce((total, question, index) => total + (answers.value[index] === question.correct_index ? 1 : 0), 0);
    isFinalSubmitted.value = true;
  }
  return { bank, currentPage, pageSize, totalPages, pageQuestions, answers, score, answeredCount, isLoading, errorMessage, isFinalSubmitted, progress, load, setAnswer, goToPage, finishExam };
}
