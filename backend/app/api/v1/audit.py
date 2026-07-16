from __future__ import annotations

# ruff: noqa: E501
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import AuditLog, UserAccount
from backend.app.domain.enums import UserRole

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditResponse(BaseModel):
    id: str
    event_type: str
    subject_type: str
    subject_id: str | None
    occurred_at: str
    metadata: str | None


@router.get("", response_model=list[AuditResponse])
def list_audit(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.VIEWER))],
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditResponse]:
    query = select(AuditLog).order_by(AuditLog.occurred_at.desc()).limit(min(limit, 200)).offset(max(offset, 0))
    if event_type:
        query = query.where(AuditLog.event_type == event_type)
    if account.role != UserRole.SUPER_ADMIN:
        query = query.where(AuditLog.actor_person_id == account.person_id)
    return [AuditResponse(id=str(row.id), event_type=row.event_type, subject_type=row.subject_type, subject_id=str(row.subject_id) if row.subject_id else None, occurred_at=row.occurred_at.isoformat(), metadata=row.metadata_text) for row in db.scalars(query)]
