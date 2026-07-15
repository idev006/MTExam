from pathlib import Path

MAX_LINES = 800
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (
    PROJECT_ROOT / "backend",
    PROJECT_ROOT / "frontend" / "src",
    PROJECT_ROOT / "frontend" / "vite.config.ts",
)
SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".vue", ".sql"}
EXCLUDED_PARTS = {"generated", "node_modules", "dist", ".venv", "__pycache__"}


def source_files():
    for root in SOURCE_ROOTS:
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
                continue
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            yield path


def test_source_files_do_not_exceed_800_lines() -> None:
    oversized = []

    for path in source_files():
        with path.open(encoding="utf-8", errors="replace") as source_file:
            line_count = sum(1 for _ in source_file)
        if line_count > MAX_LINES:
            relative_path = path.relative_to(PROJECT_ROOT)
            oversized.append(f"{relative_path}: {line_count} lines")

    assert not oversized, "Source files exceed the 800-line limit:\n" + "\n".join(oversized)
