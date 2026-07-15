from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ScoredQuestion:
    question_id: str
    choice_ids: tuple[str, ...]
    correct_choice_id: str
    score_weight: Decimal

    def __post_init__(self) -> None:
        if not self.question_id:
            raise ValueError("Question ID must not be empty")
        if not self.choice_ids or len(self.choice_ids) != len(set(self.choice_ids)):
            raise ValueError("Choice IDs must be non-empty and unique")
        if self.correct_choice_id not in self.choice_ids:
            raise ValueError("Correct choice must belong to the question")
        if self.score_weight < Decimal(0):
            raise ValueError("Score weight must not be negative")


@dataclass(frozen=True, slots=True)
class ScoreLine:
    question_id: str
    selected_choice_id: str | None
    is_correct: bool
    awarded_score: Decimal


@dataclass(frozen=True, slots=True)
class ScoreResult:
    lines: tuple[ScoreLine, ...]
    total_score: Decimal
    maximum_score: Decimal


def deterministic_order(stable_ids: Sequence[str], *, seed: int) -> tuple[str, ...]:
    """Shuffle stable IDs with an injected seed for repeatable variant generation."""

    if len(stable_ids) != len(set(stable_ids)):
        raise ValueError("Stable IDs must be unique")
    ordered = list(stable_ids)
    random.Random(seed).shuffle(ordered)
    return tuple(ordered)


def individual_ends_at(started_at: datetime, *, duration_minutes: int) -> datetime:
    if duration_minutes <= 0:
        raise ValueError("Duration must be positive")
    return started_at + timedelta(minutes=duration_minutes)


def fixed_batch_ends_at(started_at: datetime, *, window_close_at: datetime) -> datetime:
    _ensure_comparable(started_at, window_close_at)
    if started_at >= window_close_at:
        raise ValueError("The fixed exam window has already closed")
    return window_close_at


def remaining_seconds(*, server_now: datetime, ends_at: datetime) -> int:
    _ensure_comparable(server_now, ends_at)
    return max(0, math.ceil((ends_at - server_now).total_seconds()))


def is_expired(*, server_now: datetime, ends_at: datetime) -> bool:
    _ensure_comparable(server_now, ends_at)
    return server_now >= ends_at


def score_answers(
    questions: Sequence[ScoredQuestion],
    answers: Mapping[str, str | None],
) -> ScoreResult:
    """Score by stable choice ID; display order is deliberately not an input."""

    question_ids = [question.question_id for question in questions]
    if len(question_ids) != len(set(question_ids)):
        raise ValueError("Question IDs must be unique")
    unknown_questions = set(answers) - set(question_ids)
    if unknown_questions:
        raise ValueError("Answers contain a question outside this variant")

    lines: list[ScoreLine] = []
    for question in questions:
        selected = answers.get(question.question_id)
        if selected is not None and selected not in question.choice_ids:
            raise ValueError("Selected choice does not belong to the question")
        correct = selected is not None and selected == question.correct_choice_id
        awarded = question.score_weight if correct else Decimal(0)
        lines.append(ScoreLine(question.question_id, selected, correct, awarded))

    return ScoreResult(
        lines=tuple(lines),
        total_score=sum((line.awarded_score for line in lines), start=Decimal(0)),
        maximum_score=sum((question.score_weight for question in questions), start=Decimal(0)),
    )


def _ensure_comparable(first: datetime, second: datetime) -> None:
    first_is_aware = first.tzinfo is not None and first.utcoffset() is not None
    second_is_aware = second.tzinfo is not None and second.utcoffset() is not None
    if first_is_aware != second_is_aware:
        raise ValueError("Timestamps must use the same timezone convention")
