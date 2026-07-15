from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app


def test_health_reports_database_and_version(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    assert response.json() == {
        "status": "ok",
        "app_name": "MTExam Test",
        "version": "0.1.0-test",
        "database": "sqlite",
    }


def test_public_config_exposes_only_public_values(client: TestClient) -> None:
    response = client.get("/api/v1/public-config")

    assert response.status_code == 200
    body = response.json()
    assert body["app_name"] == "MTExam Test"
    assert body["maximum_upload_size_mb"] == 20
    assert "database_url" not in body
    assert "app_secret_key" not in body


def test_not_found_uses_standard_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/not-a-route")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert response.json()["error"]["correlation_id"]


def test_built_frontend_is_served_by_application(
    test_settings: Settings,
    tmp_path,
) -> None:
    frontend_dist = tmp_path / "dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text("<title>MTExam</title>", encoding="utf-8")

    with TestClient(create_app(test_settings, frontend_dist=frontend_dist)) as static_client:
        response = static_client.get("/")

    assert response.status_code == 200
    assert "MTExam" in response.text
