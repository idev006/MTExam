# Dependency Register

## Runtime Dependencies

Python versions pin ใน requirements.txt:

- FastAPI, Uvicorn
- Pydantic and pydantic-settings
- SQLAlchemy and Alembic
- Psycopg and PyMySQL
- pwdlib/Argon2 and PyJWT
- pytest, pytest-cov, httpx2 and Ruff

SQLite driver มากับ Python

Frontend dependencies:

- Vite, Vue
- Vue Router, Pinia
- Tailwind CSS, daisyUI

package-lock.json ต้องเป็น lock SSOT หลังสร้าง frontend

## External Project Dependencies

| ID | Dependency | Provider/Owner | Needed by | Risk |
|---|---|---|---|---|
| EXT-001 | Approved sample personnel CSV | Personnel data owner | M1 | R-001 |
| EXT-002 | Organization code hierarchy | Organization owner | M1 | R-001 |
| EXT-003 | Authentication/SSO decision | Product Owner | Production | R-012 |
| EXT-004 | Hosting account/runtime limits | Operations | Deployment | R-008 |
| EXT-005 | Production database choice | Tech Lead/Operations | Load test | R-003 |
| EXT-006 | Data retention policy | Sponsor/Security | Production | R-007 |
| EXT-007 | Acceptance representatives | Product Owner | Each milestone | Delivery |

## Resolved External Dependencies

| ID | Dependency | Resolution | Date |
|---|---|---|---|
| EXT-008 | GitHub Project for shared Kanban | [MTExam Delivery](https://github.com/users/idev006/projects/3/views/1) created with 10 linked Issues | 2026-07-15 |

## Dependency Approval

- Runtime package ใหม่ต้องมี ticket/reason
- ตรวจ standard library/ของเดิมก่อนเพิ่ม
- Pin version และตรวจ license/security
- ห้ามเพิ่ม infrastructure service โดยไม่มี ADR
- Project Manager track external dependency/blocker ใน board
