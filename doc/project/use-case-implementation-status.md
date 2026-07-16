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
- Exam Creation: subject, desired question count, selected questions, variants and allowed bureaus
- Reports baseline: summary, employee CSV and per-Exam-Creation statistics
- Durable practice recovery and real exam-session API plus Vue exam lobby/session UI baseline
- Exam window management and server clock endpoint
- User administration, audit API/UI baseline and responsive role-aware UI

## Partial / Production hardening

| Use-case area | Remaining acceptance work | Priority |
|---|---|---|
| Personnel import | Row correction, reconciliation history, rollback and per-row audit | P0 |
| Authorization | Organization scope service, account lifecycle and permission matrix | P0 |
| Question Bank | Version history, bulk import, archive/restore and publish history | P1 |
| Exam Paper | Random pool, immutable snapshots, deterministic variants and preview | P0 |
| Exam Session | Enforce bureau eligibility end-to-end and complete acceptance testing | P0 |
| Scoring | Weighted rules, result API and rationale flow for real sessions | P0 |
| Reporting | Examinee result, organization/time filters and report CSV export | P1 |
| Audit | 100% mutation coverage, before/after detail, retention and export | P1 |
| Administration | Persistent settings API and complete user/role/scope UI | P1 |
| Operations | Live MySQL/PostgreSQL, authenticated load, security review and restore drill | P0 |

## Delivery rule

Every Partial row requires a linked ticket, acceptance test, sequence evidence and release evidence
before it can move to `Done`. Use this document with the Kanban board, traceability matrix and
release-readiness checklist.
