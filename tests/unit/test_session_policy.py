import pytest

from backend.app.config import Settings
from backend.app.domain.enums import UserRole
from backend.app.domain.session_policy import SessionPolicy
from backend.app.services.auth_sessions import build_session_policy

pytestmark = pytest.mark.poc


def test_session_policy_assigns_one_examinee_and_three_admin_sessions() -> None:
    policy = SessionPolicy()

    assert policy.max_sessions_for(UserRole.EXAMINEE) == 1
    assert policy.max_sessions_for(UserRole.SUPER_ADMIN) == 3
    assert policy.max_sessions_for(UserRole.DIVISION_ADMIN) == 3
    assert policy.max_sessions_for(UserRole.EXAM_AUTHOR) == 1


def test_session_policy_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError, match="positive"):
        SessionPolicy(max_sessions_examinee=0)


def test_typed_auth_settings_build_the_runtime_policy() -> None:
    policy = build_session_policy(Settings().auth)

    assert policy.max_sessions_examinee == 1
    assert policy.max_sessions_admin == 3
    assert policy.session_expire_minutes == 480
    assert policy.session_idle_minutes == 30
