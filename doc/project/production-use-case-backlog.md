# Production Use-Case Backlog

**Updated:** 2026-07-16  
**Status:** MVP vertical slices are implemented; the following items remain before a production go/no-go decision.

The formal decision rationale and release gates are recorded in [Production Go/No-Go Decision](production-go-decision.md).

## P0 release blockers

| ID | Use-case area | Remaining acceptance outcome |
|---|---|---|
| P0-ORG-IMPORT | Personnel import | Row-level correction and reconciliation UI remain; persistent batch rollback endpoint is now implemented |
| P0-AUTH-SCOPE | Authorization | Scope is enforced for personnel, question banks, papers, windows, reports and audit; scope-assignment API is implemented, UI and full matrix acceptance remain |
| P0-PAPER | Exam Paper | Immutable snapshots, deterministic seeded variants, random-pool mode and paper preview are implemented; criteria acceptance remains |
| P0-SESSION | Exam Session | Result-detail UI, rationale display, pagination/page-size, offline retry queue and boundary acceptance tests |
| P0-SCORE | Scoring | Configurable scoring policy, stable result API contract and rationale UI acceptance |
| P0-DB | Operations | PostgreSQL 16 and MySQL 8.4 migration/startup smoke verified; authenticated 500-user load and performance tuning remain |
| P0-SEC | Security | Security smoke baseline is automated; independent penetration test and production security sign-off remain |

## P1 before broad rollout

| ID | Use-case area | Remaining acceptance outcome |
|---|---|---|
| P1-QBANK | Question Bank | Version history, bulk import, archive/restore and publish history |
| P1-REPORT | Reporting | Scoped exam-session XLSX export added; detailed PDF and complete organization/time report acceptance remain |
| P1-AUDIT | Audit | 100% mutation coverage, before/after detail, retention and export |
| P1-ADMIN | Administration | Persistent settings API and complete user/role/scope UI |

## Conditional dependency

| ID | Use-case area | Condition |
|---|---|---|
| SSO-001 | Police SSO | Starts when the Identity Provider contract is approved: OIDC/SAML metadata, claims mapping, certificates and logout endpoint |

## Already implemented baseline

Login/logout, server sessions, session limits, CSRF, login throttling, role checks, account lifecycle
revocation, PDPA bank, question authoring baseline, scoped paper/window baseline, immutable paper
snapshots, deterministic variants, start/resume/answer/submit, weighted score, scoped reports,
PDF/XLSX summary, scoped/paginated audit baseline, personnel/station seed data and SQLite restore
drill are implemented. The current authenticated load smoke evidence is 100 requests / 10 workers
against `/health`; it is not a substitute for the agreed 500-user production profile.

An item moves to Done only when its UI/API path, authorization, persistence, failure path, automated
test, sequence evidence and operational acceptance are all attached to the Kanban ticket.
