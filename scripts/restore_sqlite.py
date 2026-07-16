"""SQLite backup/restore drill for the minimal deployment profile."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def backup(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_db, sqlite3.connect(target) as target_db:
        source_db.backup(target_db)
    check(target)


def check(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if result != ("ok",):
        raise SystemExit(f"SQLite integrity check failed: {result}")
    print(f"SQLite integrity check passed: {database}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("source", type=Path)
    backup_parser.add_argument("target", type=Path)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("database", type=Path)
    args = parser.parse_args()
    if args.command == "backup":
        backup(args.source, args.target)
    else:
        check(args.database)


if __name__ == "__main__":
    main()
