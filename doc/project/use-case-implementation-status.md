# Use-Case Implementation Status

**As of:** 2026-07-16  
**Overall:** MVP vertical slices implemented; Production use cases remain in hardening

This document is the implementation view of the actor/use-case catalog. `Implemented MVP`
means the core API/UI path exists and has automated evidence. It does not mean the complete
Production acceptance gate is closed.

## Implemented MVP

- Authentication: login, logout, `/auth/me`, cookie sessions and session limits
- Subject and organization lookup, including ภ.6 bureau seed data
- Question Bank: subject-bound bank, question/choice creation, validation and publish
- Development seed: PDPA-TH-50 bank with 50 questions, four choices, correct answer and explanation
- Development end-to-end seed: 10 employees, demo bureau assignment, published 10-question paper, open batch window, and one submitted session with 10 answer records (score 7/10)
- Exam Creation: subject, desired question count, selected questions, variants and allowed bureaus
- Reports baseline: summary, employee CSV and per-Exam-Creation statistics
- Durable practice recovery and real exam-session API plus Vue exam lobby/session UI baseline
- Exam window management and server clock endpoint
- Shared question-bank metadata with exam-window bureau scope and configurable late-entry grace minutes
- PDF system-summary export and dependency-free XLSX system-summary export
- User administration, audit API/UI baseline and responsive role-aware UI
- Authentication hardening: persistent login throttling, CSRF protection for production cookie requests, password change, fail-closed role validation and immediate session revocation on account lifecycle changes
- Organization scope enforcement for personnel listing, question banks, papers, exam windows, reports and audit visibility
- Paper snapshots: immutable question versions and deterministic seeded question/choice ordering for all configured variants
- Personnel import rollback endpoint with batch snapshot and audit event
- Paper preview endpoint and scoped exam-session XLSX export
- Admin scope-assignment API for replacing a user’s active organization assignments
- Random-pool paper selection with deterministic seed and preview support

## Partial / Production hardening

| Use-case area | Remaining acceptance work | Priority |
|---|---|---|
| Personnel import | Row correction, reconciliation history, rollback and per-row audit | P0 |
| Authorization | Scope enforcement and account lifecycle baseline implemented; complete permission-matrix acceptance and administrative scope-assignment UI remain | P0 |
| Question Bank | Version history, bulk import, archive/restore and publish history | P1 |
| Exam Paper | Immutable snapshots and deterministic variants implemented; random-pool criteria and author preview remain | P0 |
| Exam Session | Result-detail UI, rationale display, pagination/page-size setting, offline queue and complete acceptance testing | P0 |
| Scoring | Configurable scoring policy, result API contract and rationale UI acceptance | P0 |
| Reporting | Summary PDF/XLSX and scoped baseline implemented; examinee result, organization/time filters and detailed exports remain | P1 |
| Audit | Scoped/paginated audit baseline implemented; 100% mutation coverage, before/after detail, retention and export remain | P1 |
| Administration | Persistent settings API and complete user/role/scope UI | P1 |
| SSO | Police identity-provider adapter, claims mapping and logout integration | P0 when SSO is approved |
| Operations | Live MySQL/PostgreSQL, authenticated load and external penetration test | P0 |

## Delivery rule

Every Partial row requires a linked ticket, acceptance test, sequence evidence and release evidence
before it can move to `Done`. Use this document with the Kanban board, traceability matrix and
release-readiness checklist.
