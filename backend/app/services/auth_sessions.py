from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import AuthSettings
from backend.app.db.models import AuthSession, Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.session_policy import SessionPolicy


@dataclass(frozen=True, slots=True)
class CreatedSession:
    session_id: UUID
    raw_token: str
    expires_at: datetime
    revoked_session_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class ActiveSession:
    session_id: UUID
    user_account_id: UUID
    expires_at: datetime


def build_session_policy(settings: AuthSettings) -> SessionPolicy:
    return SessionPolicy(
        max_sessions_examinee=settings.max_sessions_examinee,
        max_sessions_admin=settings.max_sessions_admin,
        session_expire_minutes=settings.session_expire_minutes,
        session_idle_minutes=settings.session_idle_minutes,
    )


def create_session(
    db_session: Session,
    *,
    user_account_id: UUID,
    role: UserRole,
    policy: SessionPolicy,
    now: datetime,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> CreatedSession:
    """Create a session and revoke oldest active sessions over the role limit."""

    active_sessions = list(
        db_session.scalars(
            select(AuthSession)
            .where(
                AuthSession.user_account_id == user_account_id,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
            )
            .order_by(AuthSession.created_at.asc(), AuthSession.id.asc())
        )
    )
    revoke_count = max(0, len(active_sessions) - policy.max_sessions_for(role) + 1)
    revoked_ids: list[UUID] = []
    for existing in active_sessions[:revoke_count]:
        existing.revoked_at = now
        existing.revoke_reason = "session_limit"
        revoked_ids.append(existing.id)

    raw_token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(minutes=policy.session_expire_minutes)
    entity = AuthSession(
        user_account_id=user_account_id,
        token_hash=hash_session_token(raw_token),
        created_at=now,
        last_seen_at=now,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db_session.add(entity)
    db_session.flush()
    return CreatedSession(entity.id, raw_token, expires_at, tuple(revoked_ids))


def get_active_session(
    db_session: Session,
    *,
    raw_token: str,
    policy: SessionPolicy,
    now: datetime,
) -> ActiveSession | None:
    if not raw_token:
        return None
    entity = db_session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_session_token(raw_token))
    )
    if entity is None or entity.revoked_at is not None or entity.expires_at <= now:
        return None

    account = db_session.get(UserAccount, entity.user_account_id)
    person = db_session.get(Person, account.person_id) if account is not None else None
    if (
        account is None
        or account.status != ActiveStatus.ACTIVE
        or person is None
        or person.status != ActiveStatus.ACTIVE
    ):
        entity.revoked_at = now
        entity.revoke_reason = "account_inactive"
        db_session.flush()
        return None

    idle_deadline = entity.last_seen_at + timedelta(minutes=policy.session_idle_minutes)
    if idle_deadline <= now:
        entity.revoked_at = now
        entity.revoke_reason = "idle_expired"
        db_session.flush()
        return None

    entity.last_seen_at = now
    db_session.flush()
    return ActiveSession(entity.id, entity.user_account_id, entity.expires_at)


def revoke_session(
    db_session: Session,
    *,
    session_id: UUID,
    now: datetime,
    reason: str = "logout",
) -> bool:
    entity = db_session.get(AuthSession, session_id)
    if entity is None or entity.revoked_at is not None:
        return False
    entity.revoked_at = now
    entity.revoke_reason = reason
    db_session.flush()
    return True


def hash_session_token(raw_token: str) -> str:
    if not raw_token:
        raise ValueError("Session token must not be empty")
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
