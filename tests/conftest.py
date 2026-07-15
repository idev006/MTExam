from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app={
            "name": "MTExam Test",
            "version": "0.1.0-test",
            "environment": "test",
            "api_prefix": "/api/v1",
            "cors_origins": [],
        },
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )


@pytest.fixture
def client(test_settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(test_settings)) as test_client:
        yield test_client
