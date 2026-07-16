# Roadmap

Roadmap เป็น outcome-based และปรับผ่าน Kanban replenishment ไม่ใช่คำสัญญาวันส่งมอบจนกว่าจะมี capacity estimate

## Current Status

Use-case completeness is tracked in [Use-Case Implementation Status](use-case-implementation-status.md).
MVP vertical slices are available for review; P0 Production hardening remains before release.

MVP vertical slices are implemented and in Verify. Production release remains blocked by the
hardening items in [Release Readiness Checklist](release-readiness-checklist.md): authoritative
timer, persistent import staging, complete authoring/paper workflows, audit coverage, live DB
verification, authenticated load and operational security evidence.

M0 technical implementation complete and in Verify. M1 is not Ready until personnel CSV contract
and M0 acceptance are addressed.

## M0 — Documentation and Foundation

Outcome:

- Approved baseline documents
- Repository/project board
- Backend/frontend skeleton
- app.toml settings
- Database connection and initial migration
- pytest/Ruff/800-line architecture test
- CI baseline
- Dashboard and Admin Settings POC for review

Exit:

- Health API runs through .venv
- Vue Vite shell calls API
- Tests pass
- `/settings` UI controls render without browser modal APIs

## M1 — Personnel and Identity

Outcome:

- Full snapshot CSV upload, validation, preview, apply
- Org hierarchy and assignment history
- Local auth baseline
- Role and scope enforcement

Exit:

- Import scenarios pass on supported database matrix
- No manual person CRUD

## M2 — Question Bank and Papers

Outcome:

- Bank/question CRUD and validation
- Fixed/random paper
- Question snapshots
- Variant generation and invariant tests

Exit:

- Generated paper is reproducible/auditable
- No answer leakage

## M3 — Examination

Outcome:

- Eligible windows
- Individual/fixed batch sessions
- Server timer, answer saving, reconnect
- Submit/timeout and scoring

Exit:

- Critical boundary tests pass
- Vertical UI flow works

## M4 — Reporting and Operations

Outcome:

- Examinee/admin reports
- CSV export
- Audit coverage
- Backup/deployment runbook
- Security review

Exit:

- Acceptance and operational checks pass

## M5 — Production Hardening

Outcome:

- Load test target
- Database production profile validation
- Accessibility and browser tests
- Restore drill
- Release readiness review

Exit:

- No critical open risks
- Production decision signed off

## Open Scheduling Inputs

- Team size and availability
- Approved sample CSV
- SSO/local decision
- Hosting/database choice
- Acceptance owner and production date

## 2026-07-16 Delivery Refresh

M0/MVP vertical slices are implemented and verified locally. The release remains blocked by the P0
items in [Production Use-Case Backlog](production-use-case-backlog.md), especially organization-scope
authorization, paper snapshot/variant rules, full exam-session recovery/result UI, live database/load
verification and independent security testing. SSO is conditional on the police Identity Provider contract.
