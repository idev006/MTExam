from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.config import Settings
from backend.app.db.url import ensure_sqlite_file_directory


class Database:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.engine = self._create_engine()
        self._session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @property
    def dialect(self) -> str:
        return self.engine.dialect.name

    def _create_engine(self) -> Engine:
        ensure_sqlite_file_directory(self._settings.database_url)
        url = make_url(self._settings.database_url)
        options: dict[str, Any] = {"pool_pre_ping": True}

        if url.get_backend_name() == "sqlite":
            options["connect_args"] = {"check_same_thread": False}
            if url.database in {None, "", ":memory:"}:
                options["poolclass"] = StaticPool
        else:
            options.update(
                pool_size=self._settings.database.pool_size,
                max_overflow=self._settings.database.max_overflow,
                pool_timeout=self._settings.database.pool_timeout_seconds,
            )

        engine = create_engine(url, **options)
        if url.get_backend_name() == "sqlite":
            self._enable_sqlite_foreign_keys(engine)
        return engine

    @staticmethod
    def _enable_sqlite_foreign_keys(engine: Engine) -> None:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        self.engine.dispose()
