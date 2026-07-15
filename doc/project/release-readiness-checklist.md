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
- [x] Persistent import batch/row staging with batch-id apply and idempotent review boundary
- [x] Report summary and CSV export API
- [x] Basic question-bank, paper and exam-window APIs
- [x] Server-authoritative exam-window clock endpoint with expiry closure
- [x] Audit API and baseline audit events for key mutations
- [x] pytest, Ruff, Vue type-check and Vite build pass
- [x] SQLite migration and portable DDL compilation evidence
- [x] Dependency-free HTTP load smoke evidence
- [x] Backup script and production operations runbook

## Production blockers

| Area | Status | Required before production |
|---|---|---|
| Server-authoritative timer | Partial | Connect clock to full ExamSession start/answer/timeout lifecycle |
| Personnel import | Partial | Add row-level correction and rollback transaction workflow |
| Question authoring | Partial | Add version snapshots and complete publish history |
| Paper builder | Partial | Add snapshotting and deterministic variant generation |
| Audit | Partial | Cover every state-changing API, retention policy and admin filters |
| Database portability | Configured | Execute integration suites against live MySQL and PostgreSQL services |
| Performance | Smoke only | Authenticated load test at the agreed target (initially 500 users) |
| Operations/security | Partial | Execute security review and backup/restore drill using the runbook |

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
