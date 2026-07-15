from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import verify_password
from backend.app.services.auth_sessions import (
    build_session_policy,
    create_session,
    get_active_session,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])
COOKIE_NAME = "mtexam_session"


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: UserRole


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _user_response(account: UserAccount, person: Person) -> UserResponse:
    return UserResponse(
        user_id=str(account.id),
        username=account.username_normalized,
        full_name=person.full_name,
        role=UserRole(account.role),
    )


def get_current_account(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserAccount:
    active = get_active_session(
        db,
        raw_token=request.cookies.get(COOKIE_NAME, ""),
        policy=build_session_policy(_settings(request).auth),
        now=utc_now(),
    )
    if active is None:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")
    account = db.get(UserAccount, active.user_account_id)
    if account is None:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")
    db.commit()
    return account


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    settings = _settings(request)
    normalized = payload.username.strip().lower()
    account = db.scalar(select(UserAccount).where(UserAccount.username_normalized == normalized))
    person = db.get(Person, account.person_id) if account else None
    if (
        account is None
        or person is None
        or account.status != ActiveStatus.ACTIVE
        or person.status != ActiveStatus.ACTIVE
        or not verify_password(payload.password, account.password_hash)
    ):
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    created = create_session(
        db,
        user_account_id=account.id,
        role=UserRole(account.role),
        policy=build_session_policy(settings.auth),
        now=utc_now(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    response.set_cookie(
        COOKIE_NAME,
        created.raw_token,
        httponly=True,
        secure=settings.app.environment == "production",
        samesite="lax",
        max_age=settings.auth.session_expire_minutes * 60,
        path="/",
    )
    return _user_response(account, person)


@router.get("/me", response_model=UserResponse)
def me(request: Request, db: Annotated[Session, Depends(get_db_session)]) -> UserResponse:
    active = get_active_session(
        db,
        raw_token=request.cookies.get(COOKIE_NAME, ""),
        policy=build_session_policy(_settings(request).auth),
        now=utc_now(),
    )
    if active is None:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")
    account = db.get(UserAccount, active.user_account_id)
    person = db.get(Person, account.person_id) if account else None
    if account is None or person is None:
        raise HTTPException(status_code=401, detail="กรุณาเข้าสู่ระบบ")
    db.commit()
    return _user_response(account, person)


@router.post("/logout")
def logout(
    request: Request, response: Response, db: Annotated[Session, Depends(get_db_session)]
) -> dict[str, str]:
    active = get_active_session(
        db,
        raw_token=request.cookies.get(COOKIE_NAME, ""),
        policy=build_session_policy(_settings(request).auth),
        now=utc_now(),
    )
    if active:
        revoke_session(db, session_id=active.session_id, now=utc_now())
        db.commit()
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"status": "ok"}
