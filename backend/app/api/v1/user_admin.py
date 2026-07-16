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
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import AuthSession, Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import hash_password
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/admin/users", tags=["user-admin"])


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=12, max_length=256)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole


class UserUpdate(BaseModel):
    role: UserRole | None = None
    status: ActiveStatus | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)


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


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> UserResponse:
    target = db.get(UserAccount, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == account.id and payload.status == ActiveStatus.INACTIVE:
        raise HTTPException(status_code=409, detail="Cannot deactivate the current account")
    person = db.get(Person, target.person_id)
    if person is None:
        raise HTTPException(status_code=409, detail="User person record is missing")
    before = {"role": target.role, "status": target.status, "full_name": person.full_name}
    changed_security_state = False
    if payload.role is not None and payload.role.value != target.role:
        target.role = payload.role
        changed_security_state = True
    if payload.status is not None and payload.status.value != target.status:
        target.status = payload.status
        person.status = payload.status
        person.status_reason = "admin_update"
        person.status_effective_date = utc_now().date()
        changed_security_state = True
    if payload.full_name is not None:
        person.full_name = payload.full_name.strip()
    if changed_security_state:
        for session in db.scalars(
            select(AuthSession).where(
                AuthSession.user_account_id == target.id,
                AuthSession.revoked_at.is_(None),
            )
        ):
            session.revoked_at = utc_now()
            session.revoke_reason = "account_admin_update"
    record_audit(
        db,
        actor_person_id=account.person_id,
        event_type="user.update",
        subject_type="user_account",
        subject_id=target.id,
        metadata={"before": before, "after": {"role": target.role, "status": target.status, "full_name": person.full_name}},
    )
    db.commit()
    return UserResponse(id=target.id, username=target.username_normalized, full_name=person.full_name, role=UserRole(target.role), status=target.status)


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
    for session in db.scalars(
        select(AuthSession).where(
            AuthSession.user_account_id == account.id,
            AuthSession.revoked_at.is_(None),
        )
    ):
        session.revoked_at = utc_now()
        session.revoke_reason = "account_deactivated"
    record_audit(db, actor_person_id=_account.person_id, event_type="user.deactivate", subject_type="user_account", subject_id=account.id)
    db.commit()
    return UserResponse(id=account.id, username=account.username_normalized, full_name=person.full_name if person else "", role=UserRole(account.role), status=account.status)
