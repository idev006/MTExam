from decimal import Decimal

from backend.app.domain.report_rules import not_started_count, pass_outcome, score_percentage


def test_score_percentage_and_pass_threshold_are_exam_creation_based() -> None:
    percentage = score_percentage(Decimal("7"), Decimal("10"))

    assert percentage == 70.0
    assert pass_outcome(percentage, Decimal("60")) is True
    assert pass_outcome(percentage, Decimal("75")) is False


def test_unknown_policy_and_attendance_are_not_invented() -> None:
    assert score_percentage(Decimal("1"), Decimal("0")) is None
    assert pass_outcome(80.0, None) is None
    assert not_started_count(None, 4) is None
    assert not_started_count(3, 4) == 0
