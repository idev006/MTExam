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
- Summary report: `200`
- Personnel API: `200`, 10 seeded employees
- A SQLite-only seed defect was found and fixed: the tenth dummy `emp_cid` was 14 digits;
  the seed now formats every identifier as exactly 13 digits.

## Remaining database gate

PostgreSQL integration is verified for the current schema and smoke workflow. The P0 database
gate remains open until MySQL execution and an authenticated workload test are completed.

