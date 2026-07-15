from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from backend.app.api.errors import register_exception_handlers
from backend.app.api.middleware import CorrelationIdMiddleware
from backend.app.api.router import api_router
from backend.app.config import PROJECT_ROOT, Settings, get_settings
from backend.app.db.base import Base
from backend.app.db.database import Database
from backend.app.db.models import Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import hash_password


def create_app(settings: Settings | None = None, frontend_dist: Path | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    database = Database(resolved_settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(database.engine)
        if resolved_settings.app.environment in {"development", "test"}:
            with database.session() as db:
                _seed_development_accounts(db)
        yield
        database.dispose()

    app = FastAPI(
        title=resolved_settings.app.name,
        version=resolved_settings.app.version,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.database = database
    app.add_middleware(CorrelationIdMiddleware)
    if resolved_settings.app.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_settings.app.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=resolved_settings.app.api_prefix)
    _mount_frontend_if_built(app, frontend_dist or PROJECT_ROOT / "frontend" / "dist")
    return app


def _seed_development_accounts(db) -> None:
    accounts = (
        ("demo", "demo1234", "ผู้เข้าสอบสาธิต", UserRole.EXAMINEE),
        ("superadmin", "super1234", "ผู้ดูแลระบบสาธิต", UserRole.SUPER_ADMIN),
        ("author", "author1234", "ผู้สร้างข้อสอบสาธิต", UserRole.EXAM_AUTHOR),
        ("viewer", "viewer1234", "ผู้ตรวจสอบสาธิต", UserRole.VIEWER),
    )
    for username, password, full_name, role in accounts:
        if db.scalar(select(UserAccount).where(UserAccount.username_normalized == username)):
            continue
        person = Person(
            identifier_hash=f"development-{username}",
            full_name=full_name,
            status=ActiveStatus.ACTIVE,
        )
        db.add(person)
        db.flush()
        db.add(
            UserAccount(
                person_id=person.id,
                username_normalized=username,
                password_hash=hash_password(password),
                role=role,
                status=ActiveStatus.ACTIVE,
            )
        )
    db.commit()


def _mount_frontend_if_built(app: FastAPI, frontend_dist: Path) -> None:
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


app = create_app()
