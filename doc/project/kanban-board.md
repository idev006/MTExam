# MTExam Kanban Board

**Status SSOT:** [GitHub Project — MTExam Delivery](https://github.com/users/idev006/projects/3/views/1)
**Last updated:** 2026-07-15
**Owner:** Project Manager (TBD)
**Current milestone:** M0 — Documentation and Foundation

## Policy

    Backlog → Analysis → Ready → In Progress → Review → Verify → Done

- WIP In Progress เริ่มต้นไม่เกิน 1
- Blocked เป็นสถานะพร้อมเหตุผล, owner และ next action
- ทุกการย้ายสถานะต้องอัปเดต GitHub Project; ไฟล์นี้เป็น periodic snapshot
- Ticket detail และ acceptance อยู่ใน GitHub Issue ที่เชื่อมกับ Project

## Board

| Ticket | Outcome | Priority | Status | Owner | Requirement/Doc | Blocker |
|---|---|---|---|---|---|---|
| [PM-001](https://github.com/idev006/MTExam/issues/1) | Initialize Git และ Project Tracking | High | Done | Project Manager/AI | Project Management Plan | None |
| [PM-002](https://github.com/idev006/MTExam/issues/2) | Configure Git remote และ migrate Kanban | High | Done | Project Manager | Project Management Plan | None |
| [PM-003](https://github.com/idev006/MTExam/issues/3) | Confirm Git identity และสร้าง baseline commit | High | Done | Project Manager | Project Management Plan | None |
| [DOC-001](https://github.com/idev006/MTExam/issues/4) | Review documentation baseline | High | Verify | PO/PM | doc/index.md | ผู้อนุมัติยังไม่ระบุ |
| [FOUNDATION-001](https://github.com/idev006/MTExam/issues/5) | FastAPI/config/database foundation | High | Verify | Developer/AI | Architecture docs | Human review/acceptance |
| [FOUNDATION-002](https://github.com/idev006/MTExam/issues/6) | Vite/Vue frontend foundation | High | Verify | Developer/AI | Frontend architecture | Human review/acceptance |
| [FOUNDATION-003](https://github.com/idev006/MTExam/issues/7) | pytest/Ruff/800-line/CI quality gates | High | Verify | Developer/AI | Testing strategy | Human review/acceptance |
| [DATA-001](https://github.com/idev006/MTExam/issues/8) | Portable schema/migration รวม SQLite employee table | High | Verify | Developer/AI | Data model, DATA-EMP-001 | MySQL/PostgreSQL CI not connected |
| [PER-IMP-001](https://github.com/idev006/MTExam/issues/9) | Implement personnel CSV staging/import | High | Blocked | Data Owner/Developer | PER-IMP-001 | Representative sample CSV |
| [SEC-001](https://github.com/idev006/MTExam/issues/10) | Confirm SSO/OIDC provider | High | Blocked | Product Owner | Authentication architecture | Provider decision and metadata |
| [POC-001](https://github.com/idev006/MTExam/issues/11) | Executable proof of project technology stack | High | Verify | Technical Lead/AI | Technology POC | Human review/acceptance |
| [AUTH-001](https://github.com/idev006/MTExam/issues/12) | Implement DB-backed browser sessions and concurrent-session policy | High | In progress | Backend/AI | ADR-0007, AUTH-003 | Full login/API wiring |

## Ticket Acceptance

### PM-001

- Git repository initialized on main
- .gitignore created
- Kanban board exists and is linked from index
- Remote Project migration recorded as dependency

### FOUNDATION-001

- Health API returns application/version/database status
- Typed settings load from config/app.toml and environment
- SQLAlchemy session supports configured database URL
- Backend starts using project .venv

### FOUNDATION-002

- Vite Vue TypeScript Composition API project exists
- Vue Router and Pinia registered
- Tailwind CSS and daisyUI configured
- Home view calls health API

### FOUNDATION-003

- pytest unit/API/architecture baseline passes
- Ruff passes
- Source file 800-line test exists
- CI runs backend and frontend checks

### DATA-001

- Portable core foundation models exist
- Alembic upgrade works on SQLite
- No dialect-specific types/imports in core
- Migration test passes

### POC-001

- 34 executable POC tests cover API/config/database/CSV/security/exam rules/session policy
- Existing 18 tests, Ruff, Vue type-check and Vite production build pass
- All 24 tables compile for SQLite, MySQL and PostgreSQL dialects
- External/live verification gaps are explicitly recorded and not claimed as passed

## Blocked Detail

### PER-IMP-001

- Condition: header mapping อนุมัติแล้ว แต่ยังไม่มี representative personnel CSV สำหรับยืนยัน encoding/value sets
- Owner: Data Owner / Product Owner
- Impact: M1 import implementation เริ่ม schema staging ได้ แต่ acceptance contract ยังปิดไม่ได้
- Next action: ส่ง anonymized sample CSV ที่ใช้ header `emp_*` และตัวอย่างค่า gender/status

### GitHub Project Migration — Resolved

- Project: [MTExam Delivery](https://github.com/users/idev006/projects/3/views/1)
- Migrated: 11 GitHub Issues covering Done, In progress, Verify และ Blocked work
- Columns: Backlog, Analysis, Ready, In progress, In review, Verify, Done และ Blocked
- Visibility: Private; การเปิด Public หรือเพิ่ม team access ต้องได้รับอนุมัติจาก owner
- Current status changes must be made on GitHub Project

## Resolved Delivery Dependencies

- Git identity: idev006 / thaipoliceregion6@gmail.com
- Remote: https://github.com/idev006/MTExam.git
- Baseline commit: d85a799
- Implementation verification commit: ef8752c
- Branch: main tracking origin/main

## Verification Evidence

### Backend and API

- Ruff: passed
- pytest: 52 passed, no warning (34 POC + 18 existing)
- Health API: verified with in-memory SQLite
- Public config: verified no secret/database URL exposure
- Standard error envelope and correlation ID: verified
- Built Vue static entry served by FastAPI: verified

### Database

- Initial portable migration: 20260715_0001
- SQLite upgrade → downgrade → upgrade: passed
- Alembic schema check: no new operations
- SQLite foreign key enforcement: verified
- MySQL/PostgreSQL execution: pending connected CI services
- Portable DDL compile: all 24 tables passed SQLite/MySQL/PostgreSQL dialect compilation

### Frontend

- npm clean install with lock: passed
- TypeScript/Vue type-check: passed
- Vite production build: passed
- npm audit production dependencies: 0 vulnerabilities

### Governance

- Git repository initialized on main
- GitHub Project is the current status SSOT with 11 linked Issues
- GitHub CI run [29407299728](https://github.com/idev006/MTExam/actions/runs/29407299728) passed at ef8752c
- POC GitHub CI run [29413533674](https://github.com/idev006/MTExam/actions/runs/29413533674) passed at a3e2cc2
- Source file 800-line architectural test: passed
- Requirement IDs unique and fully present in traceability: passed
