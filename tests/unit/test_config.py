import pytest
from pydantic import ValidationError

from backend.app.config import DEFAULT_SECRET, Settings


def test_settings_load_committed_toml() -> None:
    settings = Settings()

    assert settings.app.name == "MTExam"
    assert settings.app.api_prefix == "/api/v1"
    assert settings.personnel_import.mode == "full_snapshot"
    assert settings.personnel_import.columns.emp_cid == "emp_cid"
    assert settings.personnel_import.columns.emp_position_rank == "emp_position_rank"
    assert settings.exam.batch.allow_late_entry is True


def test_question_range_must_be_valid() -> None:
    with pytest.raises(ValidationError):
        Settings(
            exam={
                "minimum_questions": 10,
                "maximum_questions": 5,
            }
        )


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValidationError, match="APP_SECRET_KEY"):
        Settings(
            app={"environment": "production"},
            app_secret_key=DEFAULT_SECRET,
        )
