# MTExam Kanban Board

**Status SSOT:** ไฟล์นี้เป็น board ชั่วคราวจนกว่าจะมี GitHub remote/Project  
**Last updated:** 2026-07-15  
**Owner:** Project Manager (TBD)  
**Current milestone:** M0 — Documentation and Foundation  

## Policy

    Backlog → Analysis → Ready → In Progress → Review → Verify → Done

- WIP In Progress เริ่มต้นไม่เกิน 1
- Blocked เป็น flag พร้อมเหตุผลและ owner
- ทุกการย้ายสถานะต้องอัปเดตไฟล์นี้
- เมื่อ GitHub Project พร้อม ให้ migrate ticket/history และเปลี่ยน status SSOT

## Board

| Ticket | Outcome | Priority | Status | Owner | Requirement/Doc | Blocker |
|---|---|---|---|---|---|---|
| PM-001 | Initialize Git และ Project Tracking | High | Done | Project Manager/AI | Project Management Plan | GitHub migration tracked separately |
| PM-003 | Confirm Git identity และสร้าง baseline commit | High | Blocked | Project Manager | Project Management Plan | Existing identity ต้องยืนยัน |
| DOC-001 | Review documentation baseline | High | Verify | PO/PM | doc/index.md | ผู้อนุมัติยังไม่ระบุ |
| FOUNDATION-001 | FastAPI/config/database foundation | High | Verify | Developer/AI | Architecture docs | Human review/acceptance |
| FOUNDATION-002 | Vite/Vue frontend foundation | High | Verify | Developer/AI | Frontend architecture | Human review/acceptance |
| FOUNDATION-003 | pytest/Ruff/800-line/CI quality gates | High | Verify | Developer/AI | Testing strategy | CI requires remote push |
| DATA-001 | Portable initial database schema/migration | High | Verify | Developer/AI | Data model | MySQL/PostgreSQL CI not connected |
| PER-IMP-001 | Approve personnel CSV contract | High | Blocked | Data Owner | PER-IMP-001 | Approved sample CSV |

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

## Blocked Detail

### PER-IMP-001

- Condition: ไม่มี approved sample personnel CSV และ final column mapping
- Owner: Data Owner / Product Owner
- Impact: M1 import implementation เริ่ม schema staging ได้ แต่ acceptance contract ยังปิดไม่ได้
- Next action: ส่ง anonymized sample CSV และยืนยัน stable person identifier

### GitHub Project Migration

- Condition: ไม่มี GitHub remote/repository URL หรือ authenticated project context
- Owner: Project Manager
- Impact: ใช้ Markdown board ชั่วคราว; ไม่มี shared web board
- Next action: สร้าง/ระบุ GitHub repository แล้ว migrate tickets

### Initial Git Commit

- Condition: Git identity ปัจจุบันเป็นค่าเดิมจาก environment และยังไม่ได้รับการยืนยันสำหรับ MTExam
- Owner: Project Manager / Repository Owner
- Impact: Files อยู่ใน working tree และยังไม่มี baseline commit
- Next action: ยืนยัน user.name/user.email ที่ต้องใช้ แล้วสร้าง reviewed baseline commit

## Verification Evidence

### Backend and API

- Ruff: passed
- pytest: 14 passed, no warning
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

### Frontend

- npm clean install with lock: passed
- TypeScript/Vue type-check: passed
- Vite production build: passed
- npm audit production dependencies: 0 vulnerabilities

### Governance

- Git repository initialized on main
- Kanban board and ticket acceptance tracked
- Source file 800-line architectural test: passed
- Requirement IDs unique and fully present in traceability: passed
