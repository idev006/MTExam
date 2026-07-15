import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = PROJECT_ROOT / "backend" / "app" / "domain"
CORE_ROOT = PROJECT_ROOT / "backend" / "app"
FORBIDDEN_DOMAIN_PREFIXES = (
    "fastapi",
    "starlette",
    "sqlalchemy",
    "backend.app.api",
    "backend.app.db",
)
FORBIDDEN_DIALECT_PREFIX = "sqlalchemy.dialects"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_domain_does_not_depend_on_framework_or_database() -> None:
    violations = []
    for path in DOMAIN_ROOT.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(FORBIDDEN_DOMAIN_PREFIXES):
                violations.append(f"{path.name}: {module}")
    assert not violations, "Domain boundary violations:\n" + "\n".join(violations)


def test_core_does_not_import_database_specific_dialects() -> None:
    violations = []
    for path in CORE_ROOT.rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(FORBIDDEN_DIALECT_PREFIX):
                violations.append(f"{path.relative_to(PROJECT_ROOT)}: {module}")
    assert not violations, "Database dialect imports found:\n" + "\n".join(violations)
