from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, utc_now
from backend.app.domain.enums import ActiveStatus, UserRole


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    identifier_encrypted: Mapped[str | None] = mapped_column(String(512))
    identifier_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    rank: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default=ActiveStatus.ACTIVE)
    status_reason: Mapped[str | None] = mapped_column(String(100))
    status_effective_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class OrgUnit(Base):
    __tablename__ = "org_units"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(30))
    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("org_units.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), default=ActiveStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class PersonUnitAssignment(Base):
    __tablename__ = "person_unit_assignments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    person_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("persons.id"),
        index=True,
    )
    org_unit_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("org_units.id"),
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    person_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("persons.id"),
        unique=True,
    )
    username_normalized: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(50), default=UserRole.EXAMINEE)
    status: Mapped[str] = mapped_column(String(30), default=ActiveStatus.ACTIVE)
    must_change_password: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user_accounts.id"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    revoke_reason: Mapped[str | None] = mapped_column(String(50))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))
