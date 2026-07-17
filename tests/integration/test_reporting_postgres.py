import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.db.base import utc_now
from backend.app.db.models import (
    AuditLog,
    AuthSession,
    ExamPaper,
    ExamPaperOrgUnit,
    ExamSession,
    ExamWindow,
    ExamWindowScope,
    OrgUnit,
    Person,
    PersonUnitAssignment,
    UserAccount,
)
from backend.app.domain.security import hash_password
from backend.app.main import create_app


@pytest.mark.skipif(
    not os.getenv("MTEXAM_POSTGRES_TEST_URL"),
    reason="requires the opt-in PostgreSQL integration database",
)
def test_postgres_quota_lock_allows_only_one_concurrent_start() -> None:
    database_url = os.environ["MTEXAM_POSTGRES_TEST_URL"]
    engine = create_engine(database_url)
    suffix = uuid4().hex[:8]
    usernames = [f"quota-{suffix}-a", f"quota-{suffix}-b"]
    password = "quota-test-password"
    person_ids = []
    with Session(engine) as db:
        paper = db.scalar(
            select(ExamPaper).where(ExamPaper.title == "PDPA Demo Exam - 10 Questions")
        )
        assert paper is not None
        paper_quota = db.scalar(
            select(ExamPaperOrgUnit).where(ExamPaperOrgUnit.exam_paper_id == paper.id)
        )
        assert paper_quota is not None
        unit = db.get(OrgUnit, paper_quota.org_unit_id)
        assert unit is not None
        for username in usernames:
            person = Person(identifier_hash=f"test-{username}", full_name=username, status="active")
            db.add(person)
            db.flush()
            person_ids.append(person.id)
            db.add(
                UserAccount(
                    person_id=person.id,
                    username_normalized=username,
                    password_hash=hash_password(password),
                    role="examinee",
                    status="active",
                )
            )
            db.add(
                PersonUnitAssignment(
                    person_id=person.id, org_unit_id=unit.id, effective_from=date.today()
                )
            )
        window = ExamWindow(
            exam_paper_id=paper.id,
            title=f"Concurrent quota {suffix}",
            mode="individual",
            duration_minutes=30,
            completion_policy="fixed_end",
            late_entry_minutes=60,
            window_open_at=utc_now(),
            window_close_at=utc_now() + timedelta(hours=1),
            status="open",
            created_by=paper.created_by,
        )
        db.add(window)
        db.flush()
        window_id = window.id
        db.add(
            ExamWindowScope(
                exam_window_id=window.id,
                org_unit_id=unit.id,
                eligible_count=1,
            )
        )
        db.commit()

    settings = Settings(database_url=database_url, app_secret_key="postgres-quota-test-secret")
    clients = [TestClient(create_app(settings)), TestClient(create_app(settings))]
    try:
        for client, username in zip(clients, usernames, strict=True):
            assert (
                client.post(
                    "/api/v1/auth/login", json={"username": username, "password": password}
                ).status_code
                == 200
            )
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(
                    lambda client: client.post(f"/api/v1/exam-sessions/windows/{window_id}/start"),
                    clients,
                )
            )
        assert sorted(response.status_code for response in responses) == [201, 409]
    finally:
        for client in clients:
            client.close()
        with Session(engine) as db:
            db.execute(delete(ExamSession).where(ExamSession.exam_window_id == window_id))
            db.execute(delete(ExamWindowScope).where(ExamWindowScope.exam_window_id == window_id))
            db.execute(delete(ExamWindow).where(ExamWindow.id == window_id))
            db.execute(
                delete(AuthSession).where(
                    AuthSession.user_account_id.in_(
                        select(UserAccount.id).where(UserAccount.person_id.in_(person_ids))
                    )
                )
            )
            db.execute(
                delete(PersonUnitAssignment).where(PersonUnitAssignment.person_id.in_(person_ids))
            )
            db.execute(delete(UserAccount).where(UserAccount.person_id.in_(person_ids)))
            db.execute(delete(AuditLog).where(AuditLog.actor_person_id.in_(person_ids)))
            db.execute(delete(Person).where(Person.id.in_(person_ids)))
            db.commit()
