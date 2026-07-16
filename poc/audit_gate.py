"""Static audit coverage gate for state-changing API handlers."""

from __future__ import annotations

import ast
from pathlib import Path

DELEGATED_AUDIT_HANDLERS = {
    "personnel.py:apply_snapshot",
    "personnel.py:import_snapshot",
}

def main() -> None:
    root = Path(__file__).resolve().parents[1] / "backend" / "app" / "api" / "v1"
    mutation_handlers: list[str] = []
    audited_handlers: set[str] = set()
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = [ast.unparse(item) for item in node.decorator_list]
            mutation = any(
                any(
                    token in item
                    for token in ("router.post", "router.put", "router.patch", "router.delete")
                )
                for item in decorators
            )
            if mutation:
                name = f"{path.name}:{node.name}"
                mutation_handlers.append(name)
                if any(
                    isinstance(child, ast.Name) and child.id == "record_audit"
                    for child in ast.walk(node)
                ):
                    audited_handlers.add(name)
    missing = sorted((set(mutation_handlers) - audited_handlers) - DELEGATED_AUDIT_HANDLERS)
    delegated = sorted((set(mutation_handlers) - audited_handlers) & DELEGATED_AUDIT_HANDLERS)
    print(
        f"mutation_handlers={len(mutation_handlers)} "
        f"audited={len(audited_handlers)} missing={len(missing)}"
    )
    if delegated:
        print(f"delegated_audit={', '.join(delegated)}")
    if missing:
        print("\n".join(missing))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
