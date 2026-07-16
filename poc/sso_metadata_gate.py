"""Validate the minimum OIDC discovery contract before SSO implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

REQUIRED = {"issuer", "authorization_endpoint", "token_endpoint", "jwks_uri"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="OIDC discovery URL or local JSON file")
    args = parser.parse_args()
    if args.source.startswith("http://") or args.source.startswith("https://"):
        with urlopen(args.source, timeout=15) as response:  # noqa: S310 - explicit operator input
            payload = json.loads(response.read())
    else:
        payload = json.loads(Path(args.source).read_text(encoding="utf-8"))
    missing = sorted(REQUIRED - payload.keys())
    if missing:
        raise SystemExit(f"OIDC metadata missing: {', '.join(missing)}")
    print("OIDC metadata contract passed")


if __name__ == "__main__":
    main()
