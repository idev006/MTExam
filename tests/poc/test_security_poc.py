from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend.app.domain.enums import UserRole
from backend.app.domain.security import (
    AccessTokenError,
    OrgScope,
    Principal,
    can_administer_scope,
    decode_access_token,
    hash_password,
    issue_access_token,
    verify_password,
)

pytestmark = pytest.mark.poc
TOKEN_SECRET = "test-only-secret-key-at-least-32-bytes"
OTHER_SECRET = "different-test-secret-at-least-32-bytes"


def test_password_is_argon2id_and_verification_denies_wrong_password() -> None:
    encoded = hash_password("correct horse battery staple")

    assert encoded.startswith("$argon2id$")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)
    assert "correct horse" not in encoded


def test_jwt_round_trip_expiry_and_signature_validation() -> None:
    now = datetime.now(UTC)
    principal = Principal(
        subject="person-001",
        role=UserRole.BUREAU_ADMIN,
        scope=OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก"),
    )
    token = issue_access_token(principal, TOKEN_SECRET, now=now)

    assert decode_access_token(token, TOKEN_SECRET) == principal
    with pytest.raises(AccessTokenError):
        decode_access_token(token, OTHER_SECRET)

    expired = issue_access_token(
        principal,
        TOKEN_SECRET,
        now=now - timedelta(hours=2),
        lifetime=timedelta(minutes=1),
    )
    with pytest.raises(AccessTokenError):
        decode_access_token(expired, TOKEN_SECRET)


@pytest.mark.parametrize(
    ("role", "scope", "allowed_target", "denied_target"),
    [
        (
            UserRole.DIVISION_ADMIN,
            OrgScope(emp_bh="ภ.6"),
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก", emp_kk="สภ.เมือง"),
            OrgScope(emp_bh="ภ.5"),
        ),
        (
            UserRole.BUREAU_ADMIN,
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก"),
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก", emp_kk="สภ.เมือง"),
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.สุโขทัย"),
        ),
        (
            UserRole.STATION_ADMIN,
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก", emp_kk="สภ.เมือง"),
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก", emp_kk="สภ.เมือง"),
            OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก", emp_kk="สภ.วังทอง"),
        ),
    ],
)
def test_admin_scope_allows_descendants_and_denies_cross_scope(
    role: UserRole,
    scope: OrgScope,
    allowed_target: OrgScope,
    denied_target: OrgScope,
) -> None:
    principal = Principal("admin-001", role, scope)

    assert can_administer_scope(principal, allowed_target)
    assert not can_administer_scope(principal, denied_target)


def test_non_admin_role_is_denied_and_super_admin_is_global() -> None:
    target = OrgScope(emp_bh="ภ.6", emp_bk="ภ.จว.พิษณุโลก")

    assert not can_administer_scope(Principal("viewer", UserRole.VIEWER), target)
    assert can_administer_scope(Principal("root", UserRole.SUPER_ADMIN), target)
