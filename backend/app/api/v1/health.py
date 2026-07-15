from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError
from backend.app.api.schemas import HealthResponse
from backend.app.db.dependencies import get_db_session

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def get_health(
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> HealthResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise ApiError(
            code="SERVICE_UNAVAILABLE",
            message="Database is unavailable.",
            status_code=503,
        ) from error

    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        app_name=settings.app.name,
        version=settings.app.version,
        database=request.app.state.database.dialect,
    )
