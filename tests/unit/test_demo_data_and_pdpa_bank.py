import json
from pathlib import Path

from backend.app.dev.fake_data import build_demo_employees


def test_demo_data_is_deterministic_and_pdpa_bank_is_complete() -> None:
    first = build_demo_employees(10)
    second = build_demo_employees(10)
    assert first == second
    assert len({employee["emp_cid"] for employee in first}) == 10
    assert all(employee["emp_cid"] and employee["emp_status"] for employee in first)

    bank_path = Path(__file__).parents[2] / "data" / "question_banks" / "pdpa_50.json"
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    questions = bank["questions"]
    assert len(questions) == 50
    assert len({question["id"] for question in questions}) == 50
    assert all(len(question["choices"]) == 4 for question in questions)
    assert all(question["explanation"].strip() for question in questions)
    assert all(
        sum(index == question["correct_index"] for index in range(4)) == 1 for question in questions
    )
