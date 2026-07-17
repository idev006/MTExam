from datetime import timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from backend.app.db.base import utc_now
from backend.app.db.models import ExamAnswer, ExamSession, ExamWindow, UserAccount


def _login(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200


def _start_demo_session(client: TestClient) -> dict[str, object]:
    _login(client, "demo", "demo1234")
    windows = client.get("/api/v1/exam-windows")
    assert windows.status_code == 200
    window = next(row for row in windows.json() if row["status"] == "open")
    with client.app.state.database.session() as db:
        account = db.scalar(
            select(UserAccount).where(UserAccount.username_normalized == "demo")
        )
        assert account is not None
        existing = db.scalar(
            select(ExamSession).where(
                ExamSession.person_id == account.person_id,
                ExamSession.exam_window_id == UUID(window["id"]),
            )
        )
        if existing:
            db.execute(delete(ExamAnswer).where(ExamAnswer.exam_session_id == existing.id))
            db.delete(existing)
            db.commit()
    started = client.post(f"/api/v1/exam-sessions/windows/{window['id']}/start")
    assert started.status_code == 201
    return started.json()


def test_submit_finalizes_score_percentage_pass_state_and_is_idempotent(
    client: TestClient,
) -> None:
    started = _start_demo_session(client)

    submitted = client.post(f"/api/v1/exam-sessions/{started['id']}/submit")
    repeated = client.post(f"/api/v1/exam-sessions/{started['id']}/submit")

    assert submitted.status_code == repeated.status_code == 200
    result = submitted.json()
    assert result["status"] == "submitted"
    assert result["score"] == 0
    assert result["maximum_score"] == 10
    assert result["percentage"] == 0
    assert result["passing_percentage"] == 60
    assert result["passed"] is False
    assert result["result_visible"] is True
    assert repeated.json()["score"] == result["score"]


def test_timeout_uses_same_scoring_path_and_creates_audit_event(client: TestClient) -> None:
    started = _start_demo_session(client)
    database = client.app.state.database
    with database.session() as db:
        session = db.get(ExamSession, UUID(str(started["id"])))
        assert session is not None
        session.ends_at = utc_now() - timedelta(seconds=1)
        db.commit()

    expired = client.get(f"/api/v1/exam-sessions/{started['id']}")
    assert expired.status_code == 200
    assert expired.json()["status"] == "timed_out"
    assert expired.json()["score"] == 0
    assert expired.json()["maximum_score"] == 10

    _login(client, "superadmin", "super1234")
    audit = client.get("/api/v1/audit", params={"event_type": "exam_session.timeout"})
    assert audit.status_code == 200
    assert any(row["subject_id"] == started["id"] for row in audit.json())


def test_hidden_result_policy_withholds_score_and_rationale(client: TestClient) -> None:
    database = client.app.state.database
    with database.session() as db:
        window = db.scalar(select(ExamWindow).where(ExamWindow.status == "open"))
        assert window is not None
        window.result_visibility = "hidden"
        db.commit()

    started = _start_demo_session(client)
    submitted = client.post(f"/api/v1/exam-sessions/{started['id']}/submit")

    assert submitted.status_code == 200
    result = submitted.json()
    assert result["status"] == "submitted"
    assert result["result_visible"] is False
    assert result["score"] is None
    assert result["percentage"] is None
    assert result["passed"] is None
    assert all("explanation" not in question for question in result["questions"])


def test_result_can_be_revealed_only_after_window_closes(client: TestClient) -> None:
    database = client.app.state.database
    with database.session() as db:
        window = db.scalar(select(ExamWindow).where(ExamWindow.status == "open"))
        assert window is not None
        window.result_visibility = "after_window_close"
        db.commit()

    started = _start_demo_session(client)
    submitted = client.post(f"/api/v1/exam-sessions/{started['id']}/submit")
    assert submitted.status_code == 200
    assert submitted.json()["result_visible"] is False

    with database.session() as db:
        window = db.get(ExamWindow, UUID(str(started["exam_window_id"])))
        assert window is not None
        window.status = "closed"
        db.commit()

    revealed = client.get(f"/api/v1/exam-sessions/{started['id']}")
    assert revealed.status_code == 200
    assert revealed.json()["result_visible"] is True
    assert revealed.json()["score"] == 0


def test_only_window_manager_can_force_close_with_a_reason(client: TestClient) -> None:
    started = _start_demo_session(client)
    denied = client.post(
        f"/api/v1/exam-sessions/{started['id']}/force-close",
        json={"reason": "attempt by examinee"},
    )
    assert denied.status_code == 403

    _login(client, "coordinator", "coordinator1234")
    missing_reason = client.post(
        f"/api/v1/exam-sessions/{started['id']}/force-close",
        json={"reason": "  "},
    )
    assert missing_reason.status_code == 422
    closed = client.post(
        f"/api/v1/exam-sessions/{started['id']}/force-close",
        json={"reason": "เหตุจำเป็นทางการควบคุมสอบ"},
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "force_closed"
    assert closed.json()["score"] == 0
