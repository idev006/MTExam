import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_ROOT = PROJECT_ROOT / "doc" / "requirements"
TRACEABILITY_PATH = PROJECT_ROOT / "doc" / "traceability.md"
REQUIREMENT_PATTERN = re.compile(r"^###\s+([A-Z]+(?:-[A-Z]+)*-\d+)\s+", re.MULTILINE)


def test_requirement_ids_are_unique_and_traced() -> None:
    requirement_ids = []
    for path in REQUIREMENTS_ROOT.glob("*.md"):
        requirement_ids.extend(REQUIREMENT_PATTERN.findall(path.read_text(encoding="utf-8")))

    assert requirement_ids
    assert len(requirement_ids) == len(set(requirement_ids))

    traceability = TRACEABILITY_PATH.read_text(encoding="utf-8")
    missing = [
        requirement_id
        for requirement_id in requirement_ids
        if f"| {requirement_id} |" not in traceability
    ]
    assert not missing, f"Requirements missing from traceability: {missing}"
