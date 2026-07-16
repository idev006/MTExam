from __future__ import annotations

# The endpoint declarations are intentionally kept compact; domain validation remains typed.
# ruff: noqa: E501
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import hash_password
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/admin/users", tags=["user-admin"])


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=12, max_length=256)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole


class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: UserRole
    status: str


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> list[UserResponse]:
    rows = db.scalars(select(UserAccount).order_by(UserAccount.username_normalized))
    return [UserResponse(id=row.id, username=row.username_normalized, full_name=db.get(Person, row.person_id).full_name, role=UserRole(row.role), status=row.status) for row in rows]


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> UserResponse:
    username = payload.username.strip().lower()
    if db.scalar(select(UserAccount).where(UserAccount.username_normalized == username)):
        raise HTTPException(status_code=409, detail="Username already exists")
    person = Person(identifier_hash=f"account-{username}", full_name=payload.full_name, status=ActiveStatus.ACTIVE)
    db.add(person)
    db.flush()
    account = UserAccount(person_id=person.id, username_normalized=username, password_hash=hash_password(payload.password), role=payload.role, status=ActiveStatus.ACTIVE)
    db.add(account)
    record_audit(db, actor_person_id=_account.person_id, event_type="user.create", subject_type="user_account", subject_id=account.id, metadata={"username": username, "role": payload.role.value})
    db.commit()
    db.refresh(account)
    return UserResponse(id=account.id, username=username, full_name=person.full_name, role=payload.role, status=account.status)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> UserResponse:
    account = db.get(UserAccount, user_id)
    if account is None:
        raise HTTPException(status_code=404, detail="User not found")
    account.status = ActiveStatus.INACTIVE
    person = db.get(Person, account.person_id)
    if person:
        person.status = ActiveStatus.INACTIVE
    record_audit(db, actor_person_id=_account.person_id, event_type="user.deactivate", subject_type="user_account", subject_id=account.id)
    db.commit()
    return UserResponse(id=account.id, username=account.username_normalized, full_name=person.full_name if person else "", role=UserRole(account.role), status=account.status)
