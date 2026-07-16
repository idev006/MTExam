from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import AliasChoices, BaseModel, Field, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_TOML = PROJECT_ROOT / "config" / "app.toml"
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_SECRET = "development-only-change-me"


class AppSettings(BaseModel):
    name: str = "MTExam"
    version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api/v1"
    timezone: str = "Asia/Bangkok"
    cors_origins: list[str] = Field(default_factory=list)


class DatabasePoolSettings(BaseModel):
    pool_size: int = Field(default=10, ge=1)
    max_overflow: int = Field(default=10, ge=0)
    pool_timeout_seconds: int = Field(default=30, ge=1)


class BatchExamSettings(BaseModel):
    allow_late_entry: bool = True
    minimum_remaining_minutes: int = Field(default=5, ge=0)


class ExamSettings(BaseModel):
    default_duration_minutes: int = Field(default=60, ge=1)
    minimum_questions: int = Field(default=1, ge=1)
    maximum_questions: int = Field(default=200, ge=1)
    allow_answer_revision: bool = True
    show_result_after_submit: bool = True
    batch: BatchExamSettings = Field(default_factory=BatchExamSettings)

    @model_validator(mode="after")
    def validate_question_range(self) -> ExamSettings:
        if self.maximum_questions < self.minimum_questions:
            raise ValueError("maximum_questions must be greater than or equal to minimum_questions")
        return self


class PersonnelColumnSettings(BaseModel):
    emp_cid: str = "emp_cid"
    emp_yod: str = "emp_yod"
    emp_fname: str = "emp_fname"
    emp_lname: str = "emp_lname"
    emp_position: str = "emp_position"
    emp_position_rank: str = "emp_position_rank"
    emp_yod_rank: str = "emp_yod_rank"
    emp_gender: str = "emp_gender"
    emp_tel: str = "emp_tel"
    emp_bh: str = "emp_bh"
    emp_bk: str = "emp_bk"
    emp_kk: str = "emp_kk"
    emp_status: str = "emp_status"
    emp_descr: str = "emp_descr"


class PersonnelImportSettings(BaseModel):
    mode: Literal["full_snapshot"] = "full_snapshot"
    encoding: str = "utf-8-sig"
    delimiter: str = ","
    maximum_file_size_mb: int = Field(default=20, ge=1)
    reject_duplicate_file: bool = True
    missing_person_warning_percent: int = Field(default=10, ge=0, le=100)
    columns: PersonnelColumnSettings = Field(default_factory=PersonnelColumnSettings)


class AuditSettings(BaseModel):
    enabled: bool = True
    record_ip_address: bool = True
    record_user_agent: bool = True


class AuthSettings(BaseModel):
    max_sessions_examinee: int = Field(default=1, ge=1)
    max_sessions_admin: int = Field(default=3, ge=1)
    session_expire_minutes: int = Field(default=480, ge=5)
    session_idle_minutes: int = Field(default=30, ge=1)
    max_login_attempts: int = Field(default=5, ge=1, le=20)
    login_lockout_minutes: int = Field(default=15, ge=1, le=1440)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        frozen=True,
        populate_by_name=True,
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabasePoolSettings = Field(default_factory=DatabasePoolSettings)
    exam: ExamSettings = Field(default_factory=ExamSettings)
    personnel_import: PersonnelImportSettings = Field(default_factory=PersonnelImportSettings)
    audit: AuditSettings = Field(default_factory=AuditSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    database_url: str = Field(
        default="sqlite:///./data/mtexam.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    app_secret_key: SecretStr = Field(
        default=DEFAULT_SECRET,
        validation_alias=AliasChoices("APP_SECRET_KEY", "app_secret_key"),
    )

    @model_validator(mode="after")
    def reject_default_production_secret(self) -> Settings:
        if (
            self.app.environment == "production"
            and self.app_secret_key.get_secret_value() == DEFAULT_SECRET
        ):
            raise ValueError("APP_SECRET_KEY must be configured in production")
        if self.app.environment == "production":
            if "*" in self.app.cors_origins:
                raise ValueError("Wildcard CORS origin is not allowed in production")
            if any(urlparse(origin).scheme != "https" for origin in self.app.cors_origins):
                raise ValueError("Production CORS origins must use HTTPS")
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls, toml_file=APP_TOML),
            file_secret_settings,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
