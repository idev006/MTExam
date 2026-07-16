from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.db.base import utc_now
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import LoginAttempt, Person, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import hash_password, verify_password
from backend.app.services.auth_sessions import (
    build_session_policy,
    create_session,
    get_active_session,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])
COOKIE_NAME = "mtexam_session"
CSRF_COOKIE_NAME = "mtexam_csrf"
_DUMMY_PASSWORD_HASH = hash_password("invalid-login-password")


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)


class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: UserRole


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _user_response(account: UserAccount, person: Person) -> UserResponse:
    try:
        role = UserRole(account.role)
    except ValueError as error:
        raise HTTPException(status_code=403, detail="Account role is not authorized") from error
    return UserResponse(
        user_id=str(account.id),
        username=account.username_normalized,
        full_name=person.full_name,
        role=role,
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


def require_roles(*allowed_roles: UserRole) -> Callable:
    def dependency(
        account: Annotated[UserAccount, Depends(get_current_account)],
    ) -> UserAccount:
        try:
            role = UserRole(account.role)
        except ValueError as error:
            raise HTTPException(status_code=403, detail="Account role is not authorized") from error
        if role is not UserRole.SUPER_ADMIN and role not in allowed_roles:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์ใช้งานส่วนนี้")
        return account

    return dependency


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    settings = _settings(request)
    normalized = payload.username.strip().lower()
    client_ip = request.client.host if request.client else "unknown"
    now = utc_now()
    attempt = db.scalar(
        select(LoginAttempt).where(
            LoginAttempt.username_normalized == normalized,
            LoginAttempt.ip_address == client_ip,
        )
    )
    if attempt and attempt.locked_until and attempt.locked_until > now:
        response.headers["Retry-After"] = str(
            max(1, int((attempt.locked_until - now).total_seconds()))
        )
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts",
            headers={"Retry-After": response.headers["Retry-After"]},
        )
    account = db.scalar(select(UserAccount).where(UserAccount.username_normalized == normalized))
    person = db.get(Person, account.person_id) if account else None
    try:
        password_valid = verify_password(
            payload.password,
            account.password_hash if account else _DUMMY_PASSWORD_HASH,
        )
    except Exception:  # malformed stored hashes must fail closed, never become 500s
        password_valid = False
    if (
        account is None
        or person is None
        or account.status != ActiveStatus.ACTIVE
        or person.status != ActiveStatus.ACTIVE
        or not password_valid
    ):
        if attempt is None:
            attempt = LoginAttempt(
                username_normalized=normalized,
                ip_address=client_ip,
                failure_count=0,
                first_failed_at=now,
                last_failed_at=now,
            )
            db.add(attempt)
        attempt.failure_count += 1
        attempt.last_failed_at = now
        if attempt.failure_count >= settings.auth.max_login_attempts:
            attempt.locked_until = now + timedelta(minutes=settings.auth.login_lockout_minutes)
        db.commit()
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    if attempt is not None:
        db.delete(attempt)
        db.flush()
    created = create_session(
        db,
        user_account_id=account.id,
        role=UserRole(account.role),
        policy=build_session_policy(settings.auth),
        now=now,
        ip_address=client_ip,
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
    response.set_cookie(
        CSRF_COOKIE_NAME,
        secrets.token_urlsafe(32),
        httponly=False,
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


@router.post("/change-password", response_model=UserResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(get_current_account)],
) -> UserResponse:
    person = db.get(Person, account.person_id)
    if person is None or not verify_password(payload.current_password, account.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=422, detail="New password must be different")
    account.password_hash = hash_password(payload.new_password)
    account.must_change_password = False
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
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")
    return {"status": "ok"}
