"""Pure reporting calculations."""

from decimal import Decimal


def score_percentage(score: Decimal | None, maximum: Decimal | None) -> float | None:
    if score is None or maximum is None or maximum <= 0:
        return None
    return round(float(score / maximum * 100), 2)


def pass_outcome(percentage: float | None, threshold: Decimal | None) -> bool | None:
    if percentage is None or threshold is None:
        return None
    return percentage >= float(threshold)


def not_started_count(eligible: int | None, started: int) -> int | None:
    if eligible is None:
        return None
    return max(0, eligible - started)
