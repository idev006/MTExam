import { computed, ref } from "vue";

const PAGE_SIZE_KEY = "mtexam.exam.page-size";
const DEFAULT_PAGE_SIZE = 1;
export const EXAM_PAGE_SIZE_OPTIONS = [1, 5, 10, 20, 50] as const;
function readPageSize() {
  const value = Number(localStorage.getItem(PAGE_SIZE_KEY));
  return EXAM_PAGE_SIZE_OPTIONS.includes(value as (typeof EXAM_PAGE_SIZE_OPTIONS)[number]) ? value : DEFAULT_PAGE_SIZE;
}
const pageSize = ref(readPageSize());
export function useExamSettings() {
  function setPageSize(value: number) {
    if (!EXAM_PAGE_SIZE_OPTIONS.includes(value as (typeof EXAM_PAGE_SIZE_OPTIONS)[number])) return;
    pageSize.value = value;
    localStorage.setItem(PAGE_SIZE_KEY, String(value));
  }
  return { pageSize: computed(() => pageSize.value), setPageSize };
}
