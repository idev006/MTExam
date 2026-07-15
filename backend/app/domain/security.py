from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.app.domain.enums import UserRole

DEFAULT_ISSUER = "mtexam"
DEFAULT_AUDIENCE = "mtexam-api"
_PASSWORD_HASH = PasswordHash.recommended()


class AccessTokenError(ValueError):
    """An access token is invalid, expired, or contains unsupported claims."""


@dataclass(frozen=True, slots=True)
class OrgScope:
    emp_bh: str | None = None
    emp_bk: str | None = None
    emp_kk: str | None = None

    def __post_init__(self) -> None:
        if self.emp_bk is not None and self.emp_bh is None:
            raise ValueError("A bureau scope requires its division")
        if self.emp_kk is not None and self.emp_bk is None:
            raise ValueError("A station scope requires its bureau")


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str
    role: UserRole
    scope: OrgScope = OrgScope()


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty")
    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return _PASSWORD_HASH.verify(password, encoded_hash)


def issue_access_token(
    principal: Principal,
    secret: str,
    *,
    now: datetime | None = None,
    lifetime: timedelta = timedelta(minutes=30),
    issuer: str = DEFAULT_ISSUER,
    audience: str = DEFAULT_AUDIENCE,
) -> str:
    issued_at = _aware_utc(now or datetime.now(UTC))
    if lifetime <= timedelta(0):
        raise ValueError("Token lifetime must be positive")
    _validate_hmac_secret(secret)
    payload = {
        "sub": principal.subject,
        "role": principal.role.value,
        "scope": asdict(principal.scope),
        "iat": issued_at,
        "exp": issued_at + lifetime,
        "iss": issuer,
        "aud": audience,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(
    token: str,
    secret: str,
    *,
    issuer: str = DEFAULT_ISSUER,
    audience: str = DEFAULT_AUDIENCE,
) -> Principal:
    _validate_hmac_secret(secret)
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            issuer=issuer,
            audience=audience,
            options={"require": ["sub", "role", "scope", "iat", "exp", "iss", "aud"]},
        )
        scope_claim = payload["scope"]
        if not isinstance(scope_claim, dict):
            raise TypeError("scope must be an object")
        return Principal(
            subject=str(payload["sub"]),
            role=UserRole(payload["role"]),
            scope=OrgScope(
                emp_bh=scope_claim.get("emp_bh"),
                emp_bk=scope_claim.get("emp_bk"),
                emp_kk=scope_claim.get("emp_kk"),
            ),
        )
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise AccessTokenError("Access token is invalid or expired") from exc


def can_administer_scope(principal: Principal, target: OrgScope) -> bool:
    """Apply the initial admin hierarchy deny-by-default rule."""

    if principal.role is UserRole.SUPER_ADMIN:
        return True
    if principal.role is UserRole.DIVISION_ADMIN:
        return _matches(target.emp_bh, principal.scope.emp_bh)
    if principal.role is UserRole.BUREAU_ADMIN:
        return _matches(target.emp_bh, principal.scope.emp_bh) and _matches(
            target.emp_bk, principal.scope.emp_bk
        )
    if principal.role is UserRole.STATION_ADMIN:
        return (
            _matches(target.emp_bh, principal.scope.emp_bh)
            and _matches(target.emp_bk, principal.scope.emp_bk)
            and _matches(target.emp_kk, principal.scope.emp_kk)
        )
    return False


def _matches(target: str | None, allowed: str | None) -> bool:
    return allowed is not None and target == allowed


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Token timestamps must be timezone-aware")
    return value.astimezone(UTC)


def _validate_hmac_secret(secret: str) -> None:
    if len(secret.encode("utf-8")) < 32:
        raise ValueError("HS256 token secret must contain at least 32 bytes")
