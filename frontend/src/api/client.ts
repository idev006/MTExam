import type { ApiErrorResponse } from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiClientError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly correlationId: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(API_BASE_URL + path, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    const body = (await response.json()) as ApiErrorResponse;
    throw new ApiClientError(
      body.error?.message ?? "Request failed.",
      body.error?.code ?? "HTTP_ERROR",
      body.error?.correlation_id ?? "",
      response.status,
    );
  }

  return (await response.json()) as T;
}
