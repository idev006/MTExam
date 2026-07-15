"""Small dependency-free HTTP smoke load check for a running development API."""

from __future__ import annotations

import argparse
import concurrent.futures
import time
import urllib.request


def request(url: str) -> float:
    started = time.perf_counter()
    with urllib.request.urlopen(url, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"unexpected status {response.status}")
        response.read()
    return time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/v1/health")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        latencies = list(pool.map(request, [args.url] * args.requests))
    elapsed = time.perf_counter() - started
    print(f"requests={len(latencies)} workers={args.workers} elapsed={elapsed:.3f}s")
    p95 = sorted(latencies)[int(len(latencies) * 0.95) - 1] * 1000
    print(f"avg_ms={sum(latencies) / len(latencies) * 1000:.2f} p95_ms={p95:.2f}")


if __name__ == "__main__":
    main()
