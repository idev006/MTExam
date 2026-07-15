# Testing Strategy

## Goals

- ยืนยัน requirement และ correctness invariant
- ทำให้ refactor และเปลี่ยน UI/database ปลอดภัย
- Test รวดเร็ว อ่านง่าย และ deterministic
- pytest เป็นหลักของ System Core

## Test Pyramid

### Unit tests

- Pure domain rules
- Scoring
- Timing boundaries
- Personnel reconciliation
- Variant correctness
- Permission decisions

ไม่ใช้ database/network

### Integration tests

- SQLAlchemy models/queries
- Transactions และ constraints
- Alembic migrations
- Database portability
- CSV staging/apply

### API tests

- HTTP status and schemas
- Authentication/authorization
- Error codes
- Complete use cases

### Frontend tests

- Composables/Pinia ที่มี logic
- Critical component interactions
- Business rule หลักยังอยู่ใน Backend pytest

### E2E

เพิ่มใน hardening สำหรับ login, start exam, answer, timeout และ result

## Determinism

- Inject FixedClock
- Inject seeded random generator
- Factory data มี explicit defaults
- ห้าม test พึ่งเวลาจริงหรือ order ที่ไม่กำหนด

## Directory

    tests/
      unit/
      integration/
      api/
      architecture/
      poc/
      factories/
      conftest.py

## Database Strategy

- SQLite รันเร็วใน local
- Release/CI matrix รัน MySQL และ PostgreSQL ด้วย
- Integration database แยกจาก development database
- ทุก test rollback หรือ reset อย่างควบคุม

## Architectural Tests

- Source code file ไม่เกิน 800 lines
- Layer import rules ตามที่กำหนด
- ไม่มี forbidden dialect imports ใน core
- API routes ไม่มี direct database commit ตาม convention ที่ตรวจได้
- เอกสาร/traceability checks เพิ่มเมื่อ automation พร้อม

## Required Commands

    F:\programming\python\MTExam\.venv\Scripts\python.exe -m pytest
    F:\programming\python\MTExam\.venv\Scripts\python.exe -m pytest -m poc
    F:\programming\python\MTExam\.venv\Scripts\python.exe -m pytest tests\unit
    F:\programming\python\MTExam\.venv\Scripts\python.exe -m pytest --cov=backend\app
    F:\programming\python\MTExam\.venv\Scripts\python.exe -m ruff check .
    .\poc\run-poc.ps1

`poc` marker ใช้กับ executable technology proof ที่ต้องรันซ้ำใน local/CI ได้ ไม่ใช้แทน
requirement tests ของ feature จริง และผลที่ต้องพึ่ง external service ต้องบันทึกเป็น deferred verification

## Coverage

Coverage เป็น indicator ไม่ใช่เป้าหมายแทน correctness:

- Domain critical rules ต้องมี branch/boundary tests
- Security and authorization paths ต้องมี deny tests
- Bug fix ต้องเพิ่ม regression test
- ห้ามเขียน test ที่ assert เพียง status 200 โดยไม่ตรวจ outcome

## File-Size Test Policy

- Extensions: py, ts, js, vue, sql
- Count blank/comment ด้วย
- Exclude generated, vendor, node_modules, dist และ .venv
- Migration ที่ทีมดูแลไม่ exempt
- มากกว่า 800 lines ทำให้ test fail

## Release Gate

- Unit/API/integration ผ่าน
- Migration upgrade ผ่าน
- Supported database matrix ผ่าน
- No oversized source file
- Ruff ผ่าน
- Acceptance criteria มี test หรือ documented manual verification
- Known failure บันทึกใน risk/status report
