from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.errors import register_exception_handlers
from backend.app.api.middleware import CorrelationIdMiddleware
from backend.app.api.router import api_router
from backend.app.config import PROJECT_ROOT, Settings, get_settings
from backend.app.db.database import Database


def create_app(
    settings: Settings | None = None,
    frontend_dist: Path | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    database = Database(resolved_settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
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
    static_path = frontend_dist or PROJECT_ROOT / "frontend" / "dist"
    _mount_frontend_if_built(app, static_path)
    return app


def _mount_frontend_if_built(app: FastAPI, frontend_dist: Path) -> None:
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


app = create_app()
