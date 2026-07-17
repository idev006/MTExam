from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import OrgUnit, UserAccount
from backend.app.domain.enums import UserRole

router = APIRouter(prefix="/org-units", tags=["organization"])


class OrgUnitResponse(BaseModel):
    id: UUID
    code: str
    name: str
    level: str
    parent_id: UUID | None
    status: str


@router.get("", response_model=list[OrgUnitResponse])
def list_org_units(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.VIEWER)),
    ],
) -> list[OrgUnitResponse]:
    rows = db.scalars(select(OrgUnit).order_by(OrgUnit.name, OrgUnit.code))
    return [OrgUnitResponse.model_validate(row, from_attributes=True) for row in rows]
