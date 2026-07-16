from io import BytesIO
from zipfile import ZipFile

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


def test_exam_creation_subjects_are_loaded_from_database(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "author", "password": "author1234"}
        ).status_code
        == 200
    )
    response = client.get("/api/v1/question-banks/subjects")
    assert response.status_code == 200
    created = client.post(
        "/api/v1/question-banks/subjects",
        json={"code": "PDPA_TEST", "name": "วิชาทดสอบจากฐานข้อมูล"},
    )
    assert created.status_code == 201
    subjects = client.get("/api/v1/question-banks/subjects").json()
    assert any(subject["id"] == created.json()["id"] for subject in subjects)


def test_exam_author_can_create_exam_creation_with_policy_and_quota(
    client: TestClient,
) -> None:
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "author", "password": "author1234"}
        ).status_code
        == 200
    )
    subject = next(
        row for row in client.get("/api/v1/question-banks/subjects").json() if row["code"] == "PDPA"
    )
    questions = client.get(
        "/api/v1/question-banks/questions", params={"subject_id": subject["id"]}
    ).json()
    owner = next(
        row for row in client.get("/api/v1/org-units").json() if row["code"].startswith("BAG_")
    )

    response = client.post(
        "/api/v1/papers",
        json={
            "title": "Exam Creation API regression",
            "org_unit_id": owner["id"],
            "subject_id": subject["id"],
            "question_ids": [questions[0]["id"]],
            "desired_question_count": 1,
            "eligible_org_units": [{"org_unit_id": owner["id"], "eligible_count": 100}],
            "passing_percentage": 60,
            "variant_count": 1,
            "question_selection_mode": "random_pool",
            "pool_criteria": {"difficulty": "พื้นฐาน"},
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "title": "Exam Creation API regression",
        "status": "draft",
        "question_count": 1,
        "subject_id": subject["id"],
        "desired_question_count": 1,
        "allowed_org_unit_count": 1,
        "passing_percentage": 60.0,
    }


def test_practice_session_recovers_answers_and_submit_is_idempotent(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "demo", "password": "demo1234"}
        ).status_code
        == 200
    )
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
        assert (
            client.put(
                f"/api/v1/practice/sessions/{session_id}/answers",
                json={"question_index": question_index, "choice_index": 0},
            ).status_code
            == 200
        )
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


def test_superadmin_summary_xlsx_is_a_valid_workbook(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "superadmin", "password": "super1234"}
        ).status_code
        == 200
    )
    response = client.get("/api/v1/reports/summary.xlsx")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    with ZipFile(BytesIO(response.content)) as workbook:
        assert "xl/worksheets/sheet1.xml" in workbook.namelist()
        assert "Employee total" in workbook.read("xl/worksheets/sheet1.xml").decode()


def test_permission_matrix_denies_roles_at_api_boundary(client: TestClient) -> None:
    cases = [
        ("superadmin", "super1234", "/api/v1/admin/users", 200),
        ("author", "author1234", "/api/v1/admin/users", 403),
        ("demo", "demo1234", "/api/v1/admin/users", 403),
        ("viewer", "viewer1234", "/api/v1/admin/users", 403),
        ("author", "author1234", "/api/v1/question-banks", 200),
        ("viewer", "viewer1234", "/api/v1/question-banks", 403),
        ("demo", "demo1234", "/api/v1/question-banks", 403),
        ("viewer", "viewer1234", "/api/v1/reports/summary", 200),
        ("author", "author1234", "/api/v1/reports/summary", 403),
        ("demo", "demo1234", "/api/v1/reports/summary", 403),
        ("demo", "demo1234", "/api/v1/practice/sessions", 201),
        ("author", "author1234", "/api/v1/practice/sessions", 403),
        ("viewer", "viewer1234", "/api/v1/practice/sessions", 403),
    ]
    for username, password, path, expected in cases:
        login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
        assert login.status_code == 200
        response = (
            client.get(path)
            if path.endswith("question-banks") or path.endswith("users") or path.endswith("summary")
            else client.post(path)
        )
        assert response.status_code == expected
        client.post("/api/v1/auth/logout")
