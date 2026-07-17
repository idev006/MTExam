from __future__ import annotations

from datetime import datetime, timedelta

from backend.app.domain.enums import ExamCompletionPolicy


def session_ends_at(
    *,
    started_at: datetime,
    duration_minutes: int,
    window_close_at: datetime | None,
    completion_policy: str,
) -> datetime:
    """Calculate the immutable session deadline from the selected window policy."""
    duration_end = started_at + timedelta(minutes=duration_minutes)
    if completion_policy == ExamCompletionPolicy.FIXED_END and window_close_at is not None:
        return min(duration_end, window_close_at)
    return duration_end
