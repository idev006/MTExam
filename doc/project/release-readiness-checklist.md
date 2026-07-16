# Release Readiness Checklist

**As of:** 2026-07-16  
**Decision:** MVP/POC accepted for continued development; **Production release not approved**

`Verify` means implementation and automated evidence exist and still require human acceptance;
it is not equivalent to `Done` or Production Ready.

The detailed use-case inventory is maintained in [Use-Case Implementation Status](use-case-implementation-status.md).
The rationale for the current No-Go decision is maintained in [Production Go/No-Go Decision](production-go-decision.md).
The ordered remaining work is maintained in [Remaining Work Priority Register](remaining-work-priority.md).

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
| Personnel import | Partial | Add row-level correction UI and reconciliation acceptance; batch rollback endpoint is implemented |
| Question authoring | Partial | Add version snapshots and complete publish history |
| Paper builder | Partial | Random-pool mode, snapshot/variant baseline and preview endpoint implemented; complete criteria and UI acceptance |
| Audit | Partial | Scope/update events added; cover every state-changing API, retention policy and admin filters |
| Database portability | PostgreSQL 16 and MySQL 8.4 migration/startup smoke verified | Complete cross-database acceptance in target deployment |
| Performance | Health smoke 100/10 (p95 1.38s); authenticated PostgreSQL smoke 50/10 (p95 7.18s) | Tune authentication workload and execute agreed 500-user profile |
| Operations/security | Restore drill passed in dev PostgreSQL/MySQL containers | Define RPO/RTO, encrypted off-host backups, recurring drill and independent security review |

## Go/no-go rule

The detailed current backlog is [Production Use-Case Backlog](production-use-case-backlog.md).
No P0 row may be marked Done based on an API-only implementation; it must include UI, authorization,
failure-path, automated-test and operational evidence.

Release requires every Production blocker to be closed, acceptance-owner sign-off, and evidence
linked from the status report, Kanban board and traceability matrix.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend poc
npm.cmd run type-check
npm.cmd run build
```
