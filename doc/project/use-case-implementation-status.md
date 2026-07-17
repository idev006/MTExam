# Use-Case Implementation Status

**As of:** 2026-07-17
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
- Exam Creation: subject, desired question count, selected questions, variants, pass policy and
  hierarchical organization quota tree that prevents parent-child overlap before submit, default
  duration in minutes and creator-controlled Draft/Published/Archived lifecycle
- Draft editing with mandatory change summary, traceable revision families and guarded deletion of
  unused Scheduled/Cancelled Windows
- Reports baseline: summary, employee CSV and per-Exam-Creation statistics
- Durable practice recovery and real exam-session API plus Vue exam lobby/session UI baseline
- Exam Window management UI/API with per-round quota snapshots, fixed-end/full-duration policy,
  scheduled/open/suspended/closed/cancelled lifecycle, session counts and audit events
- Shared question-bank metadata with exam-window bureau scope and configurable late-entry grace minutes
- PDF system-summary export and dependency-free XLSX system-summary export
- User administration, audit API/UI baseline and responsive role-aware UI
- Authentication hardening: persistent login throttling, CSRF protection for production cookie requests, password change, fail-closed role validation and immediate session revocation on account lifecycle changes
- Organization scope enforcement for personnel listing, question banks, papers, exam windows, reports and audit visibility
- Region 6 reference hierarchy seed from `doc/p6-station.txt`, including the six administration
  divisions under บก.อก.ภ.6 and the documented children of บก.สส.ภ.6 and ศฝร.ภ.6
- Paper snapshots: immutable question versions and deterministic seeded question/choice ordering for all configured variants
- Personnel import rollback endpoint with batch snapshot and audit event
- Paper preview endpoint and scoped exam-session XLSX export
- Admin scope-assignment API for replacing a user’s active organization assignments
- Random-pool paper selection with deterministic seed and preview support
- Division/bureau/station admin scoped reporting: own organization plus active descendants,
  including organization-level breakdown statistics
- Role-aware reporting dashboard for all seven roles with Exam Creation pass policy, per-unit quota,
  ECharts attendance/pass-fail/organization comparison, scoped person detail and shared-filter exports

## Partial / Production hardening

| Use-case area | Remaining acceptance work | Priority |
|---|---|---|
| Personnel import | Row correction, reconciliation history, rollback and per-row audit | P0 |
| Authorization | Scope enforcement and account lifecycle baseline implemented; complete permission-matrix acceptance and administrative scope-assignment UI remain | P0 |
| Question Bank | Version history, bulk import, archive/restore and publish history | P1 |
| Exam Paper | Immutable snapshots, deterministic variants, Draft editing and revision/clone implemented; production author acceptance remains | P0 |
| Exam Session | Result-detail UI, rationale display, pagination/page-size setting, offline queue and complete acceptance testing | P0 |
| Scoring | Configurable scoring policy, result API contract and rationale UI acceptance | P0 |
| Reporting | UI/API/filter/export implementation, bundled OFL Chakra Petch PDF font and automated evidence complete; production device sign-off and load threshold remain | P1 |
| Audit | Scoped/paginated audit baseline implemented; 100% mutation coverage, before/after detail, retention and export remain | P1 |
| Administration | Persistent settings API and complete user/role/scope UI | P1 |
| SSO | Police identity-provider adapter, claims mapping and logout integration | P0 when SSO is approved |
| Operations | Live MySQL/PostgreSQL, authenticated load and external penetration test | P0 |

## Delivery rule

Every Partial row requires a linked ticket, acceptance test, sequence evidence and release evidence
before it can move to `Done`. Use this document with the Kanban board, traceability matrix and
release-readiness checklist.
