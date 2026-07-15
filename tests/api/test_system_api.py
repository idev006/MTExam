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


def test_pdpa_practice_bank_is_available_for_examinee_preview(client: TestClient) -> None:
    response = client.get("/api/v1/practice/banks/pdpa-50")

    assert response.status_code == 200
    body = response.json()
    assert body["bank_code"] == "PDPA-TH-50"
    assert len(body["questions"]) == 50
    assert body["questions"][0]["explanation"]


def test_practice_session_recovers_answers_and_submit_is_idempotent(client: TestClient) -> None:
    created = client.post("/api/v1/practice/sessions").json()
    session_id = created["session_id"]
    saved = client.put(
        f"/api/v1/practice/sessions/{session_id}/answers",
        json={"question_index": 0, "choice_index": 1},
    )
    assert saved.status_code == 200
    resumed = client.get(f"/api/v1/practice/sessions/{session_id}").json()
    assert resumed["answers"] == {"0": 1}
    for question_index in range(1, 50):
        assert client.put(
            f"/api/v1/practice/sessions/{session_id}/answers",
            json={"question_index": question_index, "choice_index": 0},
        ).status_code == 200
    submitted = client.post(f"/api/v1/practice/sessions/{session_id}/submit")
    assert submitted.status_code == 200
    repeated = client.post(f"/api/v1/practice/sessions/{session_id}/submit")
    assert repeated.status_code == 200
    assert repeated.json()["score"] == submitted.json()["score"]


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
