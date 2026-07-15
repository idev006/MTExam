# Project Status Report

**As of:** 2026-07-15
**Overall:** MVP vertical slices — Verify; Production readiness — Not ready
**Overall:** M0 Foundation — Verify

## Completed

Current verification evidence supersedes older baseline counts below: full pytest currently
passes 56 tests, Ruff passes, and Vue type-check/build pass. Historical commit and CI entries
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

This cycle added persistent personnel import batches/rows, server-authoritative exam-window clock
and expiry closure, question editing/publish validation, paper validation, mutation audit events,
and the SQLite backup/restore runbook. Full ExamSession timer integration, rollback UX, version
snapshots, live database execution and authenticated load remain release-gate work.

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

สถานะในไฟล์นี้เป็นรายงาน snapshot เท่านั้น [GitHub Project — MTExam Delivery](https://github.com/users/idev006/projects/3/views/1)
เป็น SSOT ของ current task status และไฟล์นี้ใช้สรุป periodic report
Project visibility ปัจจุบันเป็น Private; owner ต้องอนุมัติก่อนเปิด Public หรือเพิ่ม team access
