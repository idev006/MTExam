from datetime import datetime, timedelta

from backend.app.domain.window_policy import session_ends_at


def test_fixed_end_limits_session_to_window_close() -> None:
    started = datetime(2026, 7, 17, 9, 45)
    close = datetime(2026, 7, 17, 10, 0)
    assert session_ends_at(
        started_at=started,
        duration_minutes=60,
        window_close_at=close,
        completion_policy="fixed_end",
    ) == close


def test_full_duration_continues_after_start_deadline() -> None:
    started = datetime(2026, 7, 17, 9, 45)
    close = datetime(2026, 7, 17, 10, 0)
    assert session_ends_at(
        started_at=started,
        duration_minutes=60,
        window_close_at=close,
        completion_policy="full_duration",
    ) == started + timedelta(minutes=60)
