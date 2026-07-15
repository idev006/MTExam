# Release Readiness Checklist

**As of:** 2026-07-15  
**Decision:** MVP/POC accepted for continued development; **Production release not approved**

`Verify` means implementation and automated evidence exist and still require human acceptance;
it is not equivalent to `Done` or Production Ready.

## MVP evidence completed

- [x] FastAPI API core, Vue/Vite UI, SQLite and Alembic baseline
- [x] Cookie login/logout, `/auth/me`, role enforcement and session limits
- [x] Durable practice session with browser recovery, autosave and idempotent submit
- [x] PDPA practice bank with 50 questions, pagination and post-submit rationales
- [x] Role UI slices for administration, authoring, paper building, reports and audit
- [x] Personnel list and CSV preview/apply API slice
- [x] Report summary and CSV export API
- [x] Basic question-bank, paper and exam-window APIs
- [x] Audit API and baseline audit events for key mutations
- [x] pytest, Ruff, Vue type-check and Vite build pass
- [x] SQLite migration and portable DDL compilation evidence
- [x] Dependency-free HTTP load smoke evidence

## Production blockers

| Area | Status | Required before production |
|---|---|---|
| Server-authoritative timer | Open | Integrate exam-window clock with durable sessions, timeout and reconnect |
| Personnel import | Partial | Persistent staging batch, row review, confirmation, rollback and audit |
| Question authoring | Partial | Complete choice editing, validation, versioning and publish workflow |
| Paper builder | Partial | Fixed/random validation, snapshotting and variant generation |
| Audit | Partial | Cover every state-changing API, retention policy and admin filters |
| Database portability | Configured | Execute integration suites against live MySQL and PostgreSQL services |
| Performance | Smoke only | Authenticated load test at the agreed target (initially 500 users) |
| Operations/security | Open | Security review, backup/restore drill, deployment and monitoring runbook |

## Go/no-go rule

Release requires every Production blocker to be closed, acceptance-owner sign-off, and evidence
linked from the status report, Kanban board and traceability matrix.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend poc
npm.cmd run type-check
npm.cmd run build
```

