import { computed, ref } from "vue";
import { apiGet, apiRequest } from "@/api/client";
import { useExamSettings } from "@/stores/examSettings";
import type { PracticeBank, PracticeSession } from "@/types/practiceExam";

const SESSION_KEY = "mtexam.practice.pdpa.session";
const ANSWERS_KEY = "mtexam.practice.pdpa.answers";

export function usePracticeExam() {
  const bank = ref<PracticeBank | null>(null); const currentPage = ref(1); const answers = ref<Record<number, number>>(readAnswers());
  const sessionId = ref(localStorage.getItem(SESSION_KEY) ?? ""); const isFinalSubmitted = ref(false); const score = ref(0); const isLoading = ref(false); const errorMessage = ref(""); const syncState = ref<"saved" | "pending" | "offline">("saved");
  const { pageSize } = useExamSettings();
  const totalPages = computed(() => bank.value ? Math.ceil(bank.value.questions.length / pageSize.value) : 0); const pageQuestions = computed(() => bank.value?.questions.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value) ?? []); const progress = computed(() => totalPages.value ? Math.round((currentPage.value / totalPages.value) * 100) : 0); const answeredCount = computed(() => Object.keys(answers.value).length);
  function readAnswers(): Record<number, number> { try { return JSON.parse(localStorage.getItem(ANSWERS_KEY) ?? "{}"); } catch { return {}; } }
  function persistAnswers() { localStorage.setItem(ANSWERS_KEY, JSON.stringify(answers.value)); }
  async function createOrResumeSession() {
    try {
      let session: PracticeSession;
      if (sessionId.value) session = await apiGet<PracticeSession>(`/practice/sessions/${sessionId.value}`);
      else { session = await apiRequest<PracticeSession>("/practice/sessions", "POST"); sessionId.value = session.session_id; localStorage.setItem(SESSION_KEY, session.session_id); }
      answers.value = { ...session.answers, ...answers.value }; persistAnswers();
      if (session.status === "submitted") { isFinalSubmitted.value = true; score.value = session.score ?? 0; }
      syncState.value = "saved";
    } catch { syncState.value = navigator.onLine ? "pending" : "offline"; }
  }
  async function load() { isLoading.value = true; errorMessage.value = ""; try { bank.value = await apiGet<PracticeBank>("/practice/banks/pdpa-50"); await createOrResumeSession(); } catch (error) { errorMessage.value = error instanceof Error ? error.message : "โหลดข้อสอบไม่สำเร็จ"; } finally { isLoading.value = false; } }
  async function setAnswer(questionIndex: number, choiceIndex: number) { answers.value[questionIndex] = choiceIndex; persistAnswers(); syncState.value = "pending"; try { await apiRequest(`/practice/sessions/${sessionId.value}/answers`, "PUT", { question_index: questionIndex, choice_index: choiceIndex }); syncState.value = "saved"; } catch { syncState.value = navigator.onLine ? "pending" : "offline"; } }
  function goToPage(page: number) { if (page >= 1 && page <= totalPages.value) currentPage.value = page; }
  async function finishExam() { if (!bank.value || answeredCount.value !== bank.value.questions.length) return false; for (const [index, choice] of Object.entries(answers.value)) await apiRequest(`/practice/sessions/${sessionId.value}/answers`, "PUT", { question_index: Number(index), choice_index: choice }); const result = await apiRequest<PracticeSession>(`/practice/sessions/${sessionId.value}/submit`, "POST"); score.value = result.score ?? 0; isFinalSubmitted.value = true; syncState.value = "saved"; return true; }
  return { bank, currentPage, pageSize, totalPages, pageQuestions, answers, score, answeredCount, sessionId, syncState, isLoading, errorMessage, isFinalSubmitted, progress, load, setAnswer, goToPage, finishExam };
}
