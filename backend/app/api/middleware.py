from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        settings = getattr(request.app.state, "settings", None)
        if (
            settings is not None
            and settings.app.environment == "production"
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and request.cookies.get("mtexam_session")
            and not request.url.path.endswith("/auth/login")
        ):
            cookie_token = request.cookies.get("mtexam_csrf")
            header_token = request.headers.get("X-CSRF-Token")
            if not cookie_token or not header_token or cookie_token != header_token:
                return JSONResponse(
                    {"detail": "CSRF validation failed"}, status_code=403
                )
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
