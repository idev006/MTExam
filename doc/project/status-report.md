# Project Status Report

**As of:** 2026-07-17
**Overall:** MVP vertical slices — Verify; Production readiness — Not ready

Use-case completeness is tracked in [Use-Case Implementation Status](use-case-implementation-status.md).
MVP coverage exists. Organization scope, account lifecycle, paper snapshots/variants and scoped
report exports now have implementation evidence; external production gates remain.
**Overall:** M0 Foundation — Verify

## Completed

Current verification evidence supersedes older baseline counts below: full pytest, Ruff,
Vue component tests, type-check and build are the active gate. Historical commit and CI entries
are retained as audit history.

- Master Blueprint v4.0 aligned with current decisions
- Requirements baseline
- Architecture baseline
- Workflow and API conventions
- Project governance and ADR baseline
- Consolidated Project Management Plan
- Python .venv confirmed at project path
- requirements.txt created and dependency resolution dry-run passed
- Git repository initialized on main
- Repo-native Kanban tracking initialized
- FastAPI API/config/database foundation implemented
- Vite/Vue Composition API foundation implemented
- Portable initial schema and Alembic migration implemented
- pytest, Ruff, file-size architecture tests and CI workflow implemented
- Technical verification: 14 pytest passed; frontend type-check/build passed
- Baseline commit d85a799 pushed to GitHub main
- GitHub CI run 29407299728 passed at ef8752c
- GitHub Project `MTExam Delivery` created as private status SSOT
- 10 tracked GitHub Issues migrated: Done 3, Verify 5, Blocked 2
- SQLite employee table contract, model และ migration 0002 verified
- Executable technology POC implemented for API/config/database/CSV/security/exam rules/frontend
- POC runner passed: 34 POC + 20 existing tests, Ruff, Vue type-check and Vite build
- All 24 metadata tables compile for SQLite, MySQL and PostgreSQL dialects
- Database-backed browser session policy implemented: Examinee 1 session, admin 3 sessions, oldest revoke
- AUTH-001 (#12) tracked in GitHub Project as Verify; current commit contains session foundation
- POC GitHub Actions run 29413533674 passed at session implementation commit a3e2cc2
- Frontend UX foundation implemented: `PageContainer`, `PageHeader`, reusable daisyUI feedback, and user-selectable daisyUI themes.
- Dashboard preview implemented and verified locally: employee summary cards, searchable employee table, CSV import entry point, theme selection, and API health status.
- Admin Settings POC implemented at `/settings`: radio, range slider, switch, theme selector, and DaisyUI toast; persistence API remains the next integration slice.
- Project tracking snapshot now includes ADMIN-001 and FE-UX-001 for the new UI work; both remain Verify until API wiring and human review.
- Examinee practice page implemented at `/exam/pdpa`: 50-question PDPA bank, configurable questions-per-page setting, direct page navigation, durable SQLite practice session, API autosave, browser recovery copy, idempotent submit, and score/answer rationales revealed only after submission.
- Cookie-based Login/Logout and `/auth/me` are implemented; exam and settings routes require an authenticated session. Development account: `demo` / `demo1234`.
- Initial RBAC enforcement is implemented for `super_admin`, `exam_author`, `examinee`, and `viewer`; only `examinee` (plus the controlled `super_admin` override) may call practice exam session endpoints, while settings is `super_admin` only.
- Actor/use-case catalog and sequence diagrams are documented for authentication, personnel import, settings, question authoring, paper publishing, exam recovery/submit, and reporting.
- Development/Test role accounts are seeded only outside Production: `demo/demo1234`, `superadmin/super1234`, `author/author1234`, and `viewer/viewer1234`.
- EXAM-POC-001 is Verify: browser interaction tested through first answer and rationale display; production exam session/auth remains pending.

## In Progress

Current implementation is in MVP human-review and production-readiness verification. The latest
vertical slices include personnel import preview/apply, reports/CSV, question authoring, paper
builder, user administration, exam windows, audit API/UI and load-smoke tooling.

This cycle added personnel/report/audit scope filtering, account lifecycle updates with immediate
session revocation, immutable question snapshots with deterministic seeded variants, and XLSX/PDF
summary exports. Import rollback UX, detailed result exports, live database execution and
authenticated load remain release-gate work.

The real exam session API and Vue exam lobby/session wiring are now implemented for start/resume,
durable answer upsert, server-side timeout and idempotent submit; bureau eligibility and end-to-end
acceptance remain to be verified.

Reporting implementation now includes all eight roles, Exam Creation pass percentage and per-unit
quota, transaction-checked exam start capacity, shared-filter dashboard/export APIs, ECharts,
responsive filter/detail drawers and audited person/export reads. Automated verification is linked
from the traceability matrix. Local browser checks passed at 360/768/1366/1920 px without overflow
or console errors; production device sign-off and production load remain open.

- MVP vertical-slice human review and acceptance
- Production-readiness verification against `release-readiness-checklist.md`

## Not Started

- Server-authoritative timer and complete exam-window/session integration
- Persistent import staging with row review, rollback and complete audit trail
- Full authoring/paper-builder validation and versioning workflows
- MySQL/PostgreSQL live integration execution, authenticated load test, security review and backup/restore

## Current Blockers

Production is not ready. The detailed gate and owners are maintained in
[release-readiness-checklist.md](release-readiness-checklist.md). Open work includes the
server-authoritative timer, persistent import staging/rollback, complete authoring and paper
validation, full mutation audit coverage, live MySQL/PostgreSQL execution, authenticated load,
security review and backup/restore.

| ID | Blocker | Needed action | Owner |
|---|---|---|---|
| B-001 | ยังไม่มี representative sample CSV | ส่งไฟล์ตัวอย่างเพื่อยืนยัน encoding และค่า gender/status | Data owner |
| B-003 | SSO/local final decision | ตัดสินก่อน production integration | Product Owner |
| B-004 | ไม่มี MySQL/PostgreSQL test services | เชื่อม CI/containers ใน portability verification | Technical Lead |

## Next Recommended Tickets

Recent vertical slices added: personnel read/import API, scoped report summary API, question-bank authoring API, and viewer report page.

1. REVIEW-001 Human review/accept M0 implementation and POC-001 evidence
2. ADMIN-001 Connect settings page to authorized settings API
3. PER-IMP-001 Provide representative CSV and implement staging/import
4. SEC-001 Confirm SSO/OIDC provider
5. DB-VERIFY-001 Run migrations/integration suite on live MySQL and PostgreSQL
6. AUTH-001 Complete login/API wiring on the verified session foundation
7. PERF-001 Define workload and verify the 500-user target before production

## Release Readiness

Latest implementation slice includes user administration, question authoring, paper builder, import preview/apply, exam windows, report CSV/filtering, audit API/UI, and load-smoke tooling.

M0 technical baseline is ready for review. Production is not ready; product features, security review,
database matrix and load testing remain.

## Notes

## Delivery Refresh — 2026-07-16

The current implementation status is maintained in [Use-Case Implementation Status](use-case-implementation-status.md)
and the remaining production work is consolidated in [Production Use-Case Backlog](production-use-case-backlog.md).
Authentication hardening, station/sub-unit organization seed, PDPA data and SQLite restore drill are complete.
Production remains blocked by P0 import rollback, permission-matrix acceptance, random-pool preview,
live database/load verification and independent penetration testing.

สถานะในไฟล์นี้เป็นรายงาน snapshot เท่านั้น [GitHub Project — MTExam Delivery](https://github.com/users/idev006/projects/3/views/1)
เป็น SSOT ของ current task status และไฟล์นี้ใช้สรุป periodic report
Project visibility ปัจจุบันเป็น Private; owner ต้องอนุมัติก่อนเปิด Public หรือเพิ่ม team access

### UI layout update — 2026-07-16

The authenticated application shell now uses the full viewport width with responsive gutters.
This removes the previous 1152/1280 px content caps and gives reporting charts and wide tables more
usable space on notebook, desktop, and extra-wide displays. A component test protects the full-width
container contract.

### Paper Builder quota-tree update — 2026-07-16

The `/papers` Exam Creation form now presents organization quotas as a parent-child tree. Conflicting
ancestor/descendant selections are disabled with an explicit reason, sibling quotas remain available,
and a responsive summary explains shared parent coverage. Client overlap validation is additive to
the existing backend authorization and overlap enforcement.

### Region 6 organization hierarchy correction — 2026-07-17

The `doc/p6-station.txt` development/test seed now preserves the documented parent when transitioning
from provincial station sections to บก.อก.ภ.6 sub-units. This adds ฝ่ายอำนวยการ 1–6 beneath
บก.อก.ภ.6, retains the seven บก.สส.ภ.6 and four ศฝร.ภ.6 children, and completes a fresh database in
one idempotent seed pass.

### Exam Creation create-path correction — 2026-07-17

`POST /papers` now maps the API `pool_criteria` contract to the persisted
`ExamPaper.pool_criteria_text` ORM field and stores deterministic JSON. The previous keyword mismatch
raised an unhandled `TypeError` and returned `500 An unexpected error occurred` before creating the
paper. A full API regression test now covers subject, selected question, random-pool criteria, pass
percentage, and organization quota in one successful create request.

### Exam Creation duration and lifecycle — 2026-07-17

Exam authors can now set a 1–600 minute default duration while creating a paper. Exam Windows inherit
that duration when no override is supplied. The `/papers` page lists visible creations and controls
Draft, Open and Closed states through a DaisyUI confirmation modal. Backend creator authorization,
publish-readiness validation, audit logging and the rule that a creation cannot return to Draft after
an Exam Window exists are covered by automated API tests; Vue tests cover state-specific actions.

### Exam Window operational boundary — 2026-07-17

The new `/exam-windows` management page separates reusable ExamPaper configuration from actual exam
rounds. Migration `0014` backfills existing scope quotas, while new Windows snapshot editable quota
counts and enforce capacity against the Window row. Authors choose fixed-end or full-duration timing
and operate an audited Scheduled/Open/Suspended/Closed/Cancelled lifecycle. Backend owner checks,
domain deadline tests, PostgreSQL concurrent quota evidence and Vue lifecycle tests protect the flow.

Automated evidence for that slice: 71 pytest cases passed (the opt-in PostgreSQL case passed separately),
14 Vitest cases passed, Ruff/type-check/build/Alembic drift checks passed, and browser acceptance at
360/768/1366/1920 px found no overflow or console errors. The implementation audit closed four
findings: missing Window-owner validation, Paper-coupled quota locking, implicit fixed-end timing and
missing mandatory reasons for suspend/cancel. The existing ECharts chunk-size build warning remains
a non-blocking performance follow-up.

### ExamPaper Draft editing and revision — 2026-07-17

The Paper Builder now edits Drafts that have no Window, records a mandatory change summary, and
creates a numbered Draft revision for Papers with operational history. Revision lineage copies the
question set, pass/duration policy and quota template without changing the source. Authors can also
delete a mistaken Scheduled/Cancelled Window only when it has zero sessions. Backend conflicts,
cross-role denial, audit events and Vue action states are covered by automated tests.

Final verification for the revision slice: 71 pytest cases passed with the opt-in PostgreSQL case
skipped in the standard run and passed separately against Docker PostgreSQL; 18 Vitest cases,
frontend type-check/build, Ruff, file-size/traceability checks and Alembic drift checks passed.
Browser acceptance confirmed creator-scoped mutation actions and the DaisyUI revision modal without
console or API errors. An audit also corrected a capability leak where a visible paper could advertise
edit/revision actions to a non-owner even though the mutation endpoint correctly denied the request.

### Exam Coordinator separation of duties — 2026-07-17

New Exam Window scheduling now requires `exam_coordinator` or `super_admin`. Coordinators discover
only Published Paper templates intersecting their assigned organization scope, receive a filtered
quota policy, and cannot raise a Window quota above the Exam Creation template. Window list responses
carry creator-derived `can_manage` capability so scoped read access never advertises unauthorized
mutations. Authors retain creator-only lifecycle access to historical Windows but cannot create new
ones, preventing active rounds from becoming orphaned during transition. Backend permission tests,
the eight-role reporting context and frontend role-capability tests provide automated evidence.
Final verification: 71 pytest cases passed with the opt-in PostgreSQL concurrency case passed
separately, 21 Vitest cases passed, and Ruff, type-check, production build, source-size,
traceability and Alembic PostgreSQL drift checks passed. Browser acceptance for the new role remains
pending because the in-app browser rejected the recovered local error tab under its URL policy;
automated API/component evidence is complete and no browser pass is claimed.
## Status update — 2026-07-17 End-to-End Exam Workflow Hardening

- Added shared scoring finalization for submitted, timed-out and force-closed sessions.
- Added Exam Window result visibility (`immediate`, `after_window_close`, `hidden`) with backend
  withholding of score/pass/rationale.
- Added DaisyUI submit confirmation with unanswered count and responsive result summary.
- Added API permission/lifecycle tests and frontend component tests.
- Added cross-role swimlane and sequence evidence in the workflow documentation.
- Status remains `Verify`: production device, authenticated load and external security acceptance
  are not claimed complete.
