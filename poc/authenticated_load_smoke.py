"""Dependency-free authenticated API load smoke for a running MTExam service."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
import urllib.error
import urllib.request


def request(base_url: str, username: str, password: str) -> float:
    started = time.perf_counter()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    login = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=json.dumps({"username": username, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(login, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"login returned {response.status}")
    with opener.open(f"{base_url}/api/v1/reports/summary", timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"summary returned {response.status}")
        response.read()
    return time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="superadmin")
    parser.add_argument("--password", default="super1234")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(request, args.url, args.username, args.password)
            for _ in range(args.requests)
        ]
        latencies = [future.result() for future in futures]
    elapsed = time.perf_counter() - started
    p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)] * 1000
    print(f"requests={len(latencies)} workers={args.workers} elapsed={elapsed:.3f}s")
    print(f"avg_ms={sum(latencies) / len(latencies) * 1000:.2f} p95_ms={p95:.2f}")


if __name__ == "__main__":
    main()
