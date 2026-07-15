# System Architecture

## Architecture Style

MTExam เป็น API-first Modular Monolith แบบ Multi-tier แยกความรับผิดชอบชัดเจนแต่ deploy เป็น application เดียวได้

    Presentation Tier
      Vite + Vue 3 SPA
            ↓ REST /api/v1
    Application Tier
      FastAPI routes
      Application services
      Domain rules
            ↓ SQLAlchemy
    Data Tier
      SQLite | MySQL | PostgreSQL

## Principles

- FastAPI API เป็น System Core
- UI เปลี่ยนได้โดยไม่ย้าย business logic
- Database เข้าถึงได้ผ่าน Backend เท่านั้น
- Dependency ไหลจาก outer layer เข้า inner layer
- ไม่มี distributed component จนกว่าจะมีผลทดสอบรองรับความจำเป็น
- Durable state เก็บใน database
- เวลา server และ stored ends_at เป็น authority

## Logical Modules

| Module | Responsibility |
|---|---|
| Identity | Authentication, account lifecycle |
| Authorization | Role and organization scope |
| Personnel Import | Upload, stage, validate, reconcile, apply |
| Organization | Hierarchy and assignment history |
| Question Bank | Banks, questions, choices |
| Exam Paper | Selection, snapshot, variants |
| Exam Window | Schedule and eligible scopes |
| Exam Session | Start, timer, answers, submit |
| Scoring | Deterministic grading |
| Reporting | Results and aggregation |
| Audit | Security and business events |

โมดูลอยู่ใน process และ database เดียวกัน ไม่ใช่ microservices

## Runtime Requests

### Normal API

    Browser → route → service → domain/query → transaction → response

### Personnel import

    Upload → staging → validation → preview
    Confirm → reconciliation → single transaction → audit

### Exam answer

    PUT answer → authenticate → ownership/time check
               → insert/update → commit → response

## Deployment Modes

### Single-host minimal

FastAPI ให้บริการ API และ Vue dist จาก process/container เดียว ใช้ database หนึ่งตัว ไม่ต้องมี Nginx

### Split frontend

Vue dist อยู่ static host และเรียก FastAPI ที่ VITE_API_BASE_URL ใช้ CORS allowlist เฉพาะ origin ที่กำหนด

## Scalability Boundary

- Scale ขั้นแรกด้วย query/index optimization และลด request ที่ไม่จำเป็น
- SQLite ใช้กับ local/demo single instance
- MySQL/PostgreSQL ใช้ production และ concurrent writes
- ทดสอบ workload จริงก่อนเพิ่ม cache, proxy หรือหลาย API instances
- การเพิ่ม Redis หรือ queue ต้องมี ADR ใหม่

## Failure Model

- Database transaction ปกป้อง consistency
- API error ใช้ stable error code
- Import apply ล้มเหลวต้อง rollback ทั้ง batch
- Duplicate request ต้องไม่สร้าง session/answer ซ้ำ
- Client disconnect ไม่หยุดเวลาสอบและไม่ลบคำตอบที่ commit แล้ว

## Constraints

- Source code file ไม่เกิน 800 บรรทัด
- SQL อยู่ใน portable subset
- ไม่มี business rule สำคัญใน Vue
- ไม่มี manual personnel mutation
- ทุก feature มี requirement ID และ tests
