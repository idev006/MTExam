from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from backend.app.config import Settings
from backend.app.db import Base, Database
from backend.app.db.models import AuthSession, Person, UserAccount
from backend.app.domain.enums import UserRole
from backend.app.domain.session_policy import SessionPolicy
from backend.app.services.auth_sessions import (
    create_session,
    get_active_session,
    revoke_session,
)

pytestmark = pytest.mark.poc


def build_database() -> Database:
    settings = Settings(
        app={"environment": "test"},
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )
    return Database(settings)


def add_account(database: Database, username: str) -> UserAccount:
    with database.session() as session:
        person = Person(identifier_hash=f"hash-{username}", full_name=username)
        session.add(person)
        session.flush()
        account = UserAccount(
            person_id=person.id,
            username_normalized=username,
            password_hash="argon2-placeholder",
            role=UserRole.EXAMINEE,
        )
        session.add(account)
        session.commit()
        return account


def test_examinee_login_limit_revokes_oldest_session() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)
    account = add_account(database, "examinee-001")
    policy = SessionPolicy(max_sessions_examinee=1)
    first_time = datetime(2026, 7, 15, 9, 0)

    try:
        with database.session() as session:
            first = create_session(
                session,
                user_account_id=account.id,
                role=UserRole.EXAMINEE,
                policy=policy,
                now=first_time,
            )
            session.commit()
        with database.session() as session:
            second = create_session(
                session,
                user_account_id=account.id,
                role=UserRole.EXAMINEE,
                policy=policy,
                now=first_time + timedelta(minutes=1),
            )
            session.commit()

        assert second.revoked_session_ids == (first.session_id,)
        with database.session() as session:
            assert get_active_session(
                session,
                raw_token=first.raw_token,
                policy=policy,
                now=first_time + timedelta(minutes=1),
            ) is None
            assert get_active_session(
                session,
                raw_token=second.raw_token,
                policy=policy,
                now=first_time + timedelta(minutes=1),
            ) is not None
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_admin_login_limit_keeps_three_newest_sessions() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)
    account = add_account(database, "admin-001")
    policy = SessionPolicy(max_sessions_admin=3)
    start = datetime(2026, 7, 15, 9, 0)
    created = []

    try:
        for offset in range(4):
            with database.session() as session:
                created.append(
                    create_session(
                        session,
                        user_account_id=account.id,
                        role=UserRole.SUPER_ADMIN,
                        policy=policy,
                        now=start + timedelta(minutes=offset),
                    )
                )
                session.commit()

        with database.session() as session:
            active_count = session.scalar(
                select(func.count(AuthSession.id)).where(
                    AuthSession.user_account_id == account.id,
                    AuthSession.revoked_at.is_(None),
                )
            )
        assert active_count == 3
        assert created[3].revoked_session_ids == (created[0].session_id,)
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_idle_expiry_and_explicit_logout_revoke_sessions() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)
    account = add_account(database, "examinee-002")
    policy = SessionPolicy(session_idle_minutes=30)
    started = datetime(2026, 7, 15, 9, 0)

    try:
        with database.session() as session:
            created = create_session(
                session,
                user_account_id=account.id,
                role=UserRole.EXAMINEE,
                policy=policy,
                now=started,
            )
            session.commit()

        with database.session() as session:
            assert get_active_session(
                session,
                raw_token=created.raw_token,
                policy=policy,
                now=started + timedelta(minutes=31),
            ) is None
            session.commit()

        with database.session() as session:
            assert revoke_session(
                session,
                session_id=created.session_id,
                now=started + timedelta(minutes=32),
            ) is False
            session.commit()
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_session_token_is_stored_only_as_hash() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)
    account = add_account(database, "examinee-003")

    try:
        with database.session() as session:
            created = create_session(
                session,
                user_account_id=account.id,
                role=UserRole.EXAMINEE,
                policy=SessionPolicy(),
                now=datetime(2026, 7, 15, 9, 0),
            )
            stored = session.get(AuthSession, created.session_id)
            assert stored is not None
            assert stored.token_hash != created.raw_token
            assert len(stored.token_hash) == 64
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_inactive_person_revokes_an_existing_session() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)
    account = add_account(database, "examinee-004")
    policy = SessionPolicy()
    started = datetime(2026, 7, 15, 9, 0)

    try:
        with database.session() as session:
            created = create_session(
                session,
                user_account_id=account.id,
                role=UserRole.EXAMINEE,
                policy=policy,
                now=started,
            )
            session.commit()

        with database.session() as session:
            person = session.get(Person, account.person_id)
            assert person is not None
            person.status = "inactive"
            session.commit()

        with database.session() as session:
            assert get_active_session(
                session,
                raw_token=created.raw_token,
                policy=policy,
                now=started + timedelta(minutes=1),
            ) is None
            session.commit()

        with database.session() as session:
            stored = session.get(AuthSession, created.session_id)
            assert stored is not None
            assert stored.revoke_reason == "account_inactive"
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()
