import { onMounted, ref } from "vue";

import { fetchHealth } from "@/api/health";
import type { HealthResponse } from "@/types/api";

export function useHealth() {
  const health = ref<HealthResponse | null>(null);
  const errorMessage = ref("");
  const isLoading = ref(false);

  async function loadHealth(): Promise<void> {
    isLoading.value = true;
    errorMessage.value = "";

    try {
      health.value = await fetchHealth();
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "ไม่สามารถเชื่อมต่อ API ได้";
    } finally {
      isLoading.value = false;
    }
  }

  onMounted(loadHealth);

  return {
    health,
    errorMessage,
    isLoading,
    loadHealth,
  };
}
