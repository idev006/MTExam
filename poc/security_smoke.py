"""Repeatable security boundary smoke checks for the local API."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.main import app


def main() -> None:
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/reports/summary").status_code == 401
        assert client.get("/api/v1/admin/users").status_code == 401
        username = f"security-smoke-{time.time_ns()}"
        for _ in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": username, "password": "wrong"},
            )
            assert response.status_code == 401
        throttled = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "wrong"},
        )
        assert throttled.status_code == 429
        assert throttled.headers.get("Retry-After")
    print("security smoke passed: public boundary, protected boundary, login throttle")


if __name__ == "__main__":
    main()
