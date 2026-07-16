# PostgreSQL Integration Verification

**Date:** 2026-07-16  
**Image:** `postgres:16-alpine`  
**Container:** `mtexam-postgres`  
**Volume:** `mtexam_postgres_data`  
**Host port:** `5433` (container port `5432`)

## Reproducible setup

```powershell
docker compose -p mtexam up -d postgres
$env:DATABASE_URL = "postgresql+psycopg://mtexam:mtexam_dev_only_change_me@127.0.0.1:5433/mtexam"
\.venv\Scripts\python.exe -m alembic upgrade head
```

The compose file uses a named volume so the database survives container recreation.
The default password is development-only and must be replaced through environment variables
before any shared or production deployment.

## Evidence

- PostgreSQL 16 container healthcheck: passed
- Alembic migrations `20260715_0001` through `20260716_0010`: passed
- Application startup and development seed: passed
- `/api/v1/health`: `200`, database reported as `postgresql`
- `superadmin` login: `200`

Authenticated load smoke against PostgreSQL (50 login + summary requests, 10 workers) completed
without request failures: average `4147.58 ms`, p95 `7182.39 ms` on the development host. The
latency is a signal for performance tuning, not a production acceptance result.
- Summary report: `200`
- Personnel API: `200`, 10 seeded employees
- A SQLite-only seed defect was found and fixed: the tenth dummy `emp_cid` was 14 digits;
  the seed now formats every identifier as exactly 13 digits.

## MySQL cross-check

The same migration chain was executed against `mysql:8.4` in container `mtexam-mysql`, using
the named volume `mtexam_mysql_data` and host port `3307`.

- Alembic migrations through `20260716_0011`: passed
- Application startup: passed
- `/api/v1/health`: `200`, database reported as `mysql`
- `superadmin` login: `200`

## Remaining database gate

PostgreSQL and MySQL integration are verified for the current schema and smoke workflow. The P0
database gate remains open until authenticated workload testing and cross-database acceptance are
completed in the target deployment environment.
