from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.domain.exam_rules import (
    ScoredQuestion,
    deterministic_order,
    fixed_batch_ends_at,
    individual_ends_at,
    is_expired,
    remaining_seconds,
    score_answers,
)

pytestmark = pytest.mark.poc


def test_seeded_variant_order_is_deterministic_and_preserves_stable_ids() -> None:
    stable_ids = ("choice-a", "choice-b", "choice-c", "choice-d")

    first = deterministic_order(stable_ids, seed=20260715)
    second = deterministic_order(stable_ids, seed=20260715)

    assert first == second
    assert set(first) == set(stable_ids)
    assert first != deterministic_order(stable_ids, seed=42)


def test_scoring_uses_choice_id_for_every_display_order_and_is_idempotent() -> None:
    question = ScoredQuestion(
        question_id="question-1",
        choice_ids=("choice-a", "choice-b", "choice-c", "choice-d"),
        correct_choice_id="choice-c",
        score_weight=Decimal("1.25"),
    )

    for seed in range(40):
        display_order = deterministic_order(question.choice_ids, seed=seed)
        assert set(display_order) == set(question.choice_ids)
        result = score_answers((question,), {question.question_id: "choice-c"})
        assert result.total_score == Decimal("1.25")
        assert score_answers((question,), {question.question_id: "choice-c"}) == result


def test_decimal_scoring_handles_correct_wrong_and_unanswered() -> None:
    questions = (
        ScoredQuestion("q1", ("a", "b"), "a", Decimal("0.10")),
        ScoredQuestion("q2", ("c", "d"), "c", Decimal("0.20")),
        ScoredQuestion("q3", ("e", "f"), "e", Decimal("0.30")),
    )

    result = score_answers(questions, {"q1": "a", "q2": "d"})

    assert result.total_score == Decimal("0.10")
    assert result.maximum_score == Decimal("0.60")
    assert [line.awarded_score for line in result.lines] == [
        Decimal("0.10"),
        Decimal("0"),
        Decimal("0"),
    ]


def test_scoring_rejects_choice_or_question_outside_variant() -> None:
    question = ScoredQuestion("q1", ("a", "b"), "a", Decimal("1"))

    with pytest.raises(ValueError, match="choice"):
        score_answers((question,), {"q1": "outside"})
    with pytest.raises(ValueError, match="question"):
        score_answers((question,), {"outside": "a"})


def test_server_authoritative_individual_and_fixed_batch_boundaries() -> None:
    started_at = datetime(2026, 7, 15, 9, 0, 0)
    individual_end = individual_ends_at(started_at, duration_minutes=60)
    fixed_close = started_at + timedelta(minutes=45)

    assert individual_end == datetime(2026, 7, 15, 10, 0, 0)
    assert fixed_batch_ends_at(started_at, window_close_at=fixed_close) == fixed_close
    assert (
        remaining_seconds(
            server_now=fixed_close - timedelta(microseconds=1),
            ends_at=fixed_close,
        )
        == 1
    )
    assert remaining_seconds(server_now=fixed_close, ends_at=fixed_close) == 0
    assert not is_expired(server_now=fixed_close - timedelta(microseconds=1), ends_at=fixed_close)
    assert is_expired(server_now=fixed_close, ends_at=fixed_close)
    with pytest.raises(ValueError, match="closed"):
        fixed_batch_ends_at(fixed_close, window_close_at=fixed_close)
