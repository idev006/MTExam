from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.enums import UserRole

ADMIN_ROLES = frozenset(
    {
        UserRole.SUPER_ADMIN,
        UserRole.DIVISION_ADMIN,
        UserRole.BUREAU_ADMIN,
        UserRole.STATION_ADMIN,
    }
)


@dataclass(frozen=True, slots=True)
class SessionPolicy:
    """Limits for concurrently active browser sessions per account."""

    max_sessions_examinee: int = 1
    max_sessions_admin: int = 3
    max_sessions_other: int = 1
    session_expire_minutes: int = 480
    session_idle_minutes: int = 30

    def __post_init__(self) -> None:
        if min(
            self.max_sessions_examinee,
            self.max_sessions_admin,
            self.max_sessions_other,
            self.session_expire_minutes,
            self.session_idle_minutes,
        ) < 1:
            raise ValueError("Session policy values must be positive")

    def max_sessions_for(self, role: UserRole) -> int:
        if role is UserRole.EXAMINEE:
            return self.max_sessions_examinee
        if role in ADMIN_ROLES:
            return self.max_sessions_admin
        return self.max_sessions_other
