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
            "default_duration_minutes": 45,
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
        "default_duration_minutes": 45,
        "allowed_org_unit_count": 1,
        "passing_percentage": 60.0,
        "published_at": None,
        "family_id": response.json()["id"],
        "revision_number": 1,
        "based_on_paper_id": None,
        "change_summary": None,
        "window_count": 0,
        "session_count": 0,
        "can_edit": True,
        "can_revise": True,
    }
    paper_id = response.json()["id"]

    edit_payload = {
        "title": "Exam Creation API regression edited",
        "org_unit_id": owner["id"],
        "subject_id": subject["id"],
        "question_ids": [questions[0]["id"]],
        "desired_question_count": 1,
        "default_duration_minutes": 50,
        "eligible_org_units": [{"org_unit_id": owner["id"], "eligible_count": 120}],
        "passing_percentage": 65,
        "variant_count": 1,
        "question_selection_mode": "fixed_set",
        "pool_criteria": None,
        "change_summary": "ปรับเวลา เกณฑ์ผ่าน และ quota ก่อนเปิดใช้",
    }
    edited = client.patch(f"/api/v1/papers/{paper_id}", json=edit_payload)
    assert edited.status_code == 200
    assert edited.json()["title"] == edit_payload["title"]
    assert edited.json()["default_duration_minutes"] == 50
    assert edited.json()["passing_percentage"] == 65
    assert edited.json()["change_summary"] == edit_payload["change_summary"]

    opened = client.patch(f"/api/v1/papers/{paper_id}/status", json={"status": "published"})
    assert opened.status_code == 200
    assert opened.json()["status"] == "published"
    assert opened.json()["published_at"]

    back_to_draft = client.patch(
        f"/api/v1/papers/{paper_id}/status", json={"status": "draft"}
    )
    assert back_to_draft.status_code == 200
    assert back_to_draft.json()["status"] == "draft"
    assert back_to_draft.json()["published_at"] is None

    assert (
        client.patch(f"/api/v1/papers/{paper_id}/status", json={"status": "published"}).status_code
        == 200
    )
    quota_policy = client.get(f"/api/v1/papers/{paper_id}/quota-policy")
    assert quota_policy.status_code == 200
    assert quota_policy.json()["eligible_org_units"][0]["eligible_count"] == 120

    window_payload = {
        "exam_paper_id": paper_id,
        "title": "รอบทดสอบ Full duration",
        "completion_policy": "full_duration",
        "result_visibility": "after_window_close",
        "eligible_org_units": [{"org_unit_id": owner["id"], "eligible_count": 25}],
    }
    assert client.post("/api/v1/exam-windows", json=window_payload).status_code == 403

    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "superadmin", "password": "super1234"}
        ).status_code
        == 200
    )
    for index in (1, 2):
        created = client.post(
            "/api/v1/admin/users",
            json={
                "username": f"window-coordinator-{index}",
                "password": f"window-coordinator-{index}-password",
                "full_name": f"ผู้จัดรอบสอบคนที่ {index}",
                "role": "exam_coordinator",
            },
        )
        assert created.status_code == 201
        assert (
            client.put(
                f"/api/v1/admin/users/{created.json()['id']}/scope",
                json={"org_unit_ids": [owner["id"]]},
            ).status_code
            == 200
        )

    outside_unit = next(
        row
        for row in client.get("/api/v1/org-units").json()
        if row["level"] == "bureau" and row["id"] != owner["id"]
    )
    outside_coordinator = client.post(
        "/api/v1/admin/users",
        json={
            "username": "window-coordinator-outside",
            "password": "window-coordinator-outside-password",
            "full_name": "ผู้จัดรอบสอบนอกขอบเขต",
            "role": "exam_coordinator",
        },
    )
    assert outside_coordinator.status_code == 201
    assert (
        client.put(
            f"/api/v1/admin/users/{outside_coordinator.json()['id']}/scope",
            json={"org_unit_ids": [outside_unit["id"]]},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "username": "window-coordinator-outside",
                "password": "window-coordinator-outside-password",
            },
        ).status_code
        == 200
    )
    assert paper_id not in {item["id"] for item in client.get("/api/v1/papers").json()}
    assert client.get(f"/api/v1/papers/{paper_id}/quota-policy").status_code == 403
    assert client.post("/api/v1/exam-windows", json=window_payload).status_code == 403

    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "username": "window-coordinator-1",
                "password": "window-coordinator-1-password",
            },
        ).status_code
        == 200
    )
    assert client.get("/api/v1/org-units").status_code == 403
    operational_paper = next(
        item for item in client.get("/api/v1/papers").json() if item["id"] == paper_id
    )
    assert operational_paper["can_edit"] is False
    assert operational_paper["can_revise"] is False
    scoped_policy = client.get(f"/api/v1/papers/{paper_id}/quota-policy")
    assert scoped_policy.status_code == 200
    assert scoped_policy.json()["eligible_org_units"][0]["eligible_count"] == 120
    over_quota = client.post(
        "/api/v1/exam-windows",
        json={
            **window_payload,
            "eligible_org_units": [
                {"org_unit_id": owner["id"], "eligible_count": 121}
            ],
        },
    )
    assert over_quota.status_code == 422
    window = client.post("/api/v1/exam-windows", json=window_payload)
    assert window.status_code == 201
    assert window.json()["duration_minutes"] == 50
    assert window.json()["completion_policy"] == "full_duration"
    assert window.json()["result_visibility"] == "after_window_close"
    assert window.json()["eligible_org_units"] == [
        {"org_unit_id": owner["id"], "eligible_count": 25}
    ]
    assert window.json()["can_manage"] is True
    window_id = window.json()["id"]

    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "username": "window-coordinator-2",
                "password": "window-coordinator-2-password",
            },
        ).status_code
        == 200
    )
    foreign_window = next(
        item for item in client.get("/api/v1/exam-windows").json() if item["id"] == window_id
    )
    assert foreign_window["can_manage"] is False
    cross_author = client.patch(
        f"/api/v1/exam-windows/{window_id}/status", json={"status": "open"}
    )
    assert cross_author.status_code == 403
    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "username": "window-coordinator-1",
                "password": "window-coordinator-1-password",
            },
        ).status_code
        == 200
    )
    opened_window = client.patch(
        f"/api/v1/exam-windows/{window_id}/status", json={"status": "open"}
    )
    assert opened_window.status_code == 200
    assert opened_window.json()["status"] == "open"
    missing_reason = client.patch(
        f"/api/v1/exam-windows/{window_id}/status", json={"status": "suspended"}
    )
    assert missing_reason.status_code == 422
    suspended_window = client.patch(
        f"/api/v1/exam-windows/{window_id}/status",
        json={"status": "suspended", "reason": "ทดสอบระงับรับผู้เข้าสอบ"},
    )
    assert suspended_window.status_code == 200
    assert suspended_window.json()["status"] == "suspended"
    assert (
        client.patch(
            f"/api/v1/exam-windows/{window_id}/status", json={"status": "open"}
        ).status_code
        == 200
    )
    closed_window = client.patch(
        f"/api/v1/exam-windows/{window_id}/status", json={"status": "closed"}
    )
    assert closed_window.status_code == 200
    assert closed_window.json()["status"] == "closed"
    terminal_window = client.patch(
        f"/api/v1/exam-windows/{window_id}/status", json={"status": "open"}
    )
    assert terminal_window.status_code == 409

    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "author", "password": "author1234"}
        ).status_code
        == 200
    )
    closed = client.patch(f"/api/v1/papers/{paper_id}/status", json={"status": "archived"})
    assert closed.status_code == 200
    assert closed.json()["status"] == "archived"
    assert (
        client.patch(f"/api/v1/papers/{paper_id}/status", json={"status": "published"}).status_code
        == 200
    )
    blocked_draft = client.patch(
        f"/api/v1/papers/{paper_id}/status", json={"status": "draft"}
    )
    assert blocked_draft.status_code == 409
    assert blocked_draft.json()["error"]["code"] == "STATE_CONFLICT"

    blocked_edit = client.patch(f"/api/v1/papers/{paper_id}", json=edit_payload)
    assert blocked_edit.status_code == 409
    revision = client.post(
        f"/api/v1/papers/{paper_id}/revisions",
        json={"change_summary": "สร้างฉบับใหม่เพื่อแก้ไขหลังใช้งานจริง"},
    )
    assert revision.status_code == 201
    revision_id = revision.json()["id"]
    assert revision.json()["status"] == "draft"
    assert revision.json()["revision_number"] == 2
    assert revision.json()["family_id"] == paper_id
    assert revision.json()["based_on_paper_id"] == paper_id
    assert revision.json()["can_edit"] is True
    revision_edit = client.get(f"/api/v1/papers/{revision_id}/edit")
    assert revision_edit.status_code == 200
    assert revision_edit.json()["question_ids"] == [questions[0]["id"]]
    assert revision_edit.json()["eligible_org_units"][0]["eligible_count"] == 120

    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "username": "window-coordinator-1",
                "password": "window-coordinator-1-password",
            },
        ).status_code
        == 200
    )
    disposable = client.post(
        "/api/v1/exam-windows",
        json={"exam_paper_id": paper_id, "title": "รอบที่สร้างผิดสำหรับทดสอบลบ"},
    )
    assert disposable.status_code == 201
    deleted = client.delete(f"/api/v1/exam-windows/{disposable.json()['id']}")
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"
    cannot_delete_used_state = client.delete(f"/api/v1/exam-windows/{window_id}")
    assert cannot_delete_used_state.status_code == 409

    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "superadmin", "password": "super1234"}
        ).status_code
        == 200
    )
    audit_events = client.get(
        "/api/v1/audit", params={"event_type": "paper.status_change"}
    )
    assert audit_events.status_code == 200
    assert any(event["subject_id"] == paper_id for event in audit_events.json())
    window_events = client.get(
        "/api/v1/audit", params={"event_type": "exam_window.status_change"}
    )
    assert window_events.status_code == 200
    assert any(event["subject_id"] == window_id for event in window_events.json())
    assert client.get("/api/v1/audit", params={"event_type": "paper.edit"}).json()
    assert client.get("/api/v1/audit", params={"event_type": "paper.revision_create"}).json()
    assert client.get("/api/v1/audit", params={"event_type": "exam_window.delete"}).json()

    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "demo", "password": "demo1234"}
        ).status_code
        == 200
    )
    denied = client.patch(f"/api/v1/papers/{paper_id}/status", json={"status": "archived"})
    assert denied.status_code == 403


def test_exam_author_can_assign_exam_creation_quota_to_descendant_org(
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
    org_units = client.get("/api/v1/org-units").json()
    parent = next(row for row in org_units if row["code"].startswith("BAG_"))
    child = next(row for row in org_units if row["parent_id"] == parent["id"])

    response = client.post(
        "/api/v1/papers",
        json={
            "title": "Exam Creation descendant quota",
            "org_unit_id": parent["id"],
            "subject_id": subject["id"],
            "question_ids": [questions[0]["id"]],
            "desired_question_count": 1,
            "default_duration_minutes": 45,
            "eligible_org_units": [{"org_unit_id": child["id"], "eligible_count": 50}],
            "passing_percentage": 60,
            "variant_count": 1,
            "question_selection_mode": "fixed_set",
            "pool_criteria": None,
        },
    )

    assert response.status_code == 201
    quota_policy = client.get(f"/api/v1/papers/{response.json()['id']}/quota-policy")
    assert quota_policy.status_code == 200
    assert quota_policy.json()["eligible_org_units"] == [
        {
            "org_unit_id": child["id"],
            "org_unit_name": child["name"],
            "eligible_count": 50,
        }
    ]

    overlapped = client.post(
        "/api/v1/papers",
        json={
            "title": "Exam Creation overlapping quota",
            "org_unit_id": parent["id"],
            "subject_id": subject["id"],
            "question_ids": [questions[0]["id"]],
            "desired_question_count": 1,
            "default_duration_minutes": 45,
            "eligible_org_units": [
                {"org_unit_id": parent["id"], "eligible_count": 100},
                {"org_unit_id": child["id"], "eligible_count": 50},
            ],
            "passing_percentage": 60,
            "variant_count": 1,
            "question_selection_mode": "fixed_set",
            "pool_criteria": None,
        },
    )
    assert overlapped.status_code == 422


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
