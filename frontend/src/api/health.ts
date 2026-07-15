import { apiGet } from "@/api/client";
import type { HealthResponse } from "@/types/api";

export function fetchHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/health");
}
