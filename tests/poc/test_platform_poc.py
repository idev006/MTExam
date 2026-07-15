from __future__ import annotations

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.schema import CreateTable

from backend.app.config import PROJECT_ROOT, Settings, get_settings
from backend.app.db import Base, Database
from backend.app.db.models import Employee
from backend.app.main import create_app

pytestmark = pytest.mark.poc


def test_api_core_openapi_errors_correlation_cors_and_static_delivery(tmp_path) -> None:
    settings = Settings(
        app={
            "name": "MTExam POC",
            "version": "poc",
            "environment": "test",
            "cors_origins": ["https://allowed.example"],
        },
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )
    frontend_dist = tmp_path / "dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text("<title>MTExam POC</title>", encoding="utf-8")

    with TestClient(create_app(settings, frontend_dist=frontend_dist)) as client:
        health = client.get("/api/v1/health")
        missing = client.get("/api/v1/not-a-route")
        openapi = client.get("/openapi.json")
        preflight = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://allowed.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        frontend = client.get("/")

    assert health.status_code == 200
    assert health.headers["X-Correlation-ID"]
    assert missing.json()["error"]["correlation_id"]
    assert openapi.json()["info"] == {"title": "MTExam POC", "version": "poc"}
    assert preflight.headers["access-control-allow-origin"] == "https://allowed.example"
    assert "MTExam POC" in frontend.text


def test_toml_settings_are_typed_env_overrides_and_secrets_stay_private(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./data/poc-override.db")
    settings = Settings()

    assert settings.app.name == "MTExam"
    assert settings.exam.default_duration_minutes == 60
    assert settings.database_url.endswith("poc-override.db")

    with TestClient(create_app(settings)) as client:
        public = client.get("/api/v1/public-config").json()
    assert "database_url" not in public
    assert "app_secret_key" not in public


@pytest.mark.parametrize("dialect", [sqlite.dialect(), mysql.dialect(), postgresql.dialect()])
def test_all_tables_compile_for_all_supported_sql_dialects(dialect) -> None:
    assert len(Base.metadata.sorted_tables) == 27
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert table.name in ddl


@pytest.mark.parametrize(
    ("database_url", "expected_dialect"),
    [
        ("sqlite:///:memory:", "sqlite"),
        ("mysql+pymysql://user:password@localhost/mtexam", "mysql"),
        ("postgresql+psycopg://user:password@localhost/mtexam", "postgresql"),
    ],
)
def test_database_url_switches_installed_driver_without_application_code_change(
    database_url: str,
    expected_dialect: str,
) -> None:
    settings = Settings(
        app={"environment": "test"},
        database_url=database_url,
        app_secret_key="test-only-secret",
    )
    database = Database(settings)

    try:
        assert database.dialect == expected_dialect
    finally:
        database.dispose()


def test_sqlite_transaction_rolls_back_the_whole_unit_of_work() -> None:
    settings = Settings(
        app={"environment": "test"},
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )
    database = Database(settings)
    Employee.__table__.create(database.engine)

    try:
        with pytest.raises(RuntimeError, match="force rollback"):
            with database.session() as session:
                session.add(
                    Employee(
                        emp_cid="1234567890123",
                        emp_fname="สมชาย",
                        emp_lname="ทดสอบ",
                    )
                )
                session.flush()
                raise RuntimeError("force rollback")

        with database.session() as session:
            assert session.scalar(select(Employee)) is None
    finally:
        Employee.__table__.drop(database.engine)
        database.dispose()


def test_alembic_sqlite_upgrade_downgrade_upgrade_and_drift_check(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "poc-migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("APP_SECRET_KEY", "test-only-secret")
    get_settings.cache_clear()
    config = Config(PROJECT_ROOT / "alembic.ini")

    try:
        command.upgrade(config, "head")
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        command.check(config)
    finally:
        get_settings.cache_clear()
