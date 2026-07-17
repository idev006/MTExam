from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.db.models import OrgUnit, QuestionBank, Subject, UserAccount
from backend.app.main import create_app


def test_development_seed_can_keep_master_data_without_demo_content() -> None:
    settings = Settings(
        app={
            "name": "MTExam Seed Policy Test",
            "environment": "development",
            "cors_origins": [],
        },
        database_url="sqlite:///:memory:",
        app_secret_key="seed-policy-test-secret",
        development_seed={"master_data": True, "demo_content": False},
    )

    with TestClient(create_app(settings)) as client:
        with client.app.state.database.session() as db:
            assert db.query(UserAccount).count() == 8
            assert db.query(OrgUnit).count() > 0
            assert db.query(Subject).count() > 0
            assert db.query(QuestionBank).count() == 0
