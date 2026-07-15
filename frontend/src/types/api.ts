export interface HealthResponse {
  status: "ok";
  app_name: string;
  version: string;
  database: string;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  field_errors: Array<{
    field: string;
    code: string;
    message: string;
  }>;
  correlation_id: string;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}
