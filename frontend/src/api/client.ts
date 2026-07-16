import type { ApiErrorResponse } from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

function csrfToken(): string | undefined {
  return document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("mtexam_csrf="))
    ?.split("=")[1];
}

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
    credentials: "include",
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

export async function apiRequest<T>(path: string, method: "POST" | "PUT", body?: unknown): Promise<T> {
  const token = csrfToken();
  const response = await fetch(API_BASE_URL + path, {
    method,
    credentials: "include",
    headers: { Accept: "application/json", "Content-Type": "application/json", ...(token ? { "X-CSRF-Token": token } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = (await response.json()) as ApiErrorResponse;
    throw new ApiClientError(payload.error?.message ?? "Request failed.", payload.error?.code ?? "HTTP_ERROR", payload.error?.correlation_id ?? "", response.status);
  }
  return (await response.json()) as T;
}
