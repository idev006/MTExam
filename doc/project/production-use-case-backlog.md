# Production Use-Case Backlog

**Updated:** 2026-07-16  
**Status:** MVP vertical slices are implemented; the following items remain before a production go/no-go decision.

## P0 release blockers

| ID | Use-case area | Remaining acceptance outcome |
|---|---|---|
| P0-ORG-IMPORT | Personnel import | Row correction, reconciliation history, rollback and per-row audit |
| P0-AUTH-SCOPE | Authorization | Scope baseline now enforced for question banks, papers and exam windows; extend to personnel/reports/audit and complete account lifecycle and permission matrix |
| P0-PAPER | Exam Paper | Random pool, immutable snapshots, deterministic variants and preview |
| P0-SESSION | Exam Session | Result-detail UI, rationale display, pagination/page-size, offline retry queue and boundary acceptance tests |
| P0-SCORE | Scoring | Configurable scoring policy, stable result API contract and rationale UI acceptance |
| P0-DB | Operations | Live MySQL/PostgreSQL migration/integration verification and authenticated load test |
| P0-SEC | Security | Independent penetration test and production security sign-off |

## P1 before broad rollout

| ID | Use-case area | Remaining acceptance outcome |
|---|---|---|
| P1-QBANK | Question Bank | Version history, bulk import, archive/restore and publish history |
| P1-REPORT | Reporting | Examinee result, organization/time filters, detailed PDF and Excel export |
| P1-AUDIT | Audit | 100% mutation coverage, before/after detail, retention and export |
| P1-ADMIN | Administration | Persistent settings API and complete user/role/scope UI |

## Conditional dependency

| ID | Use-case area | Condition |
|---|---|---|
| SSO-001 | Police SSO | Starts when the Identity Provider contract is approved: OIDC/SAML metadata, claims mapping, certificates and logout endpoint |

## Already implemented baseline

Login/logout, server sessions, session limits, CSRF, login throttling, role checks, PDPA bank,
question authoring baseline, paper/window baseline, start/resume/answer/submit, weighted score,
PDF summary, audit baseline, personnel/station seed data and SQLite restore drill are implemented.

An item moves to Done only when its UI/API path, authorization, persistence, failure path, automated
test, sequence evidence and operational acceptance are all attached to the Kanban ticket.
