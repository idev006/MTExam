"""Validate restore-gate evidence without exposing backup contents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--restore-report", type=Path, required=True)
    parser.add_argument("--rpo-minutes", type=float, required=True)
    parser.add_argument("--rto-seconds", type=float, required=True)
    parser.add_argument("--max-rpo-minutes", type=float, default=15)
    parser.add_argument("--max-rto-seconds", type=float, default=900)
    args = parser.parse_args()
    if not args.backup.exists() or not args.restore_report.exists():
        raise SystemExit("backup and restore-report files are required")
    if args.rpo_minutes > args.max_rpo_minutes or args.rto_seconds > args.max_rto_seconds:
        raise SystemExit("RPO/RTO threshold failed")
    report = json.loads(args.restore_report.read_text(encoding="utf-8"))
    if report.get("status") != "passed" or report.get("backup_sha256") != sha256(args.backup):
        raise SystemExit("restore report status or backup checksum failed")
    if not report.get("encrypted_off_host_backup", False):
        raise SystemExit("encrypted_off_host_backup sign-off is required")
    print("restore gate passed")


if __name__ == "__main__":
    main()
