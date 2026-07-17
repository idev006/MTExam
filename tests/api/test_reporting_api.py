from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str) -> None:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200


def test_reporting_context_is_available_to_all_eight_roles(client: TestClient) -> None:
    accounts = [
        ("superadmin", "super1234"),
        ("viewer", "viewer1234"),
        ("divisionadmin", "division1234"),
        ("bureauadmin", "bureau1234"),
        ("stationadmin", "station1234"),
        ("author", "author1234"),
        ("coordinator", "coordinator1234"),
        ("demo", "demo1234"),
    ]
    for username, password in accounts:
        login(client, username, password)
        response = client.get("/api/v1/reports/context")
        assert response.status_code == 200
        assert response.json()["role"]
        client.post("/api/v1/auth/logout")


def test_dashboard_uses_exam_creation_policy_and_scoped_breakdown(client: TestClient) -> None:
    login(client, "superadmin", "super1234")
    context = client.get("/api/v1/reports/context").json()
    response = client.get(
        "/api/v1/reports/dashboard",
        params={"exam_paper_id": context["default_exam_paper_id"], "page_size": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["passing_percentage"] == 60.0
    assert body["kpis"]["eligible"] == 10
    assert body["kpis"]["submitted"] == 1
    assert body["kpis"]["passed"] == 1
    assert body["organizations"][0]["eligible"] == 10


def test_examinee_can_only_open_own_report_detail(client: TestClient) -> None:
    login(client, "demo", "demo1234")
    own = client.get("/api/v1/reports/my-results")
    assert own.status_code == 200
    assert len(own.json()) == 1
    detail = client.get(f"/api/v1/reports/people/{own.json()[0]['session_id']}")
    assert detail.status_code == 200
    assert detail.json()["session"]["person_id"] == own.json()[0]["person_id"]


def test_author_analytics_and_viewer_denial(client: TestClient) -> None:
    login(client, "author", "author1234")
    paper_id = client.get("/api/v1/reports/context").json()["default_exam_paper_id"]
    response = client.get("/api/v1/reports/question-analytics", params={"exam_paper_id": paper_id})
    assert response.status_code == 200
    client.post("/api/v1/auth/logout")
    login(client, "viewer", "viewer1234")
    denied = client.get("/api/v1/reports/question-analytics", params={"exam_paper_id": paper_id})
    assert denied.status_code == 403


def test_filtered_csv_export_has_bom_and_creates_audit_event(client: TestClient) -> None:
    login(client, "superadmin", "super1234")
    paper_id = client.get("/api/v1/reports/context").json()["default_exam_paper_id"]
    exported = client.get(
        "/api/v1/reports/export", params={"format": "csv", "exam_paper_id": paper_id}
    )
    assert exported.status_code == 200
    assert exported.content.startswith(b"\xef\xbb\xbf")
    events = client.get("/api/v1/audit", params={"event_type": "report.export"})
    assert events.status_code == 200
    assert any(row["event_type"] == "report.export" for row in events.json())


def test_filtered_pdf_embeds_thai_capable_chakra_petch(client: TestClient) -> None:
    login(client, "superadmin", "super1234")
    paper_id = client.get("/api/v1/reports/context").json()["default_exam_paper_id"]
    exported = client.get(
        "/api/v1/reports/export", params={"format": "pdf", "exam_paper_id": paper_id}
    )

    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/pdf"
    assert b"ChakraPetch" in exported.content
