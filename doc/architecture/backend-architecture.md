# Backend Architecture

## Runtime

- Python 3.12
- Interpreter: F:\programming\python\MTExam\.venv\Scripts\python.exe
- FastAPI
- Synchronous SQLAlchemy session
- Alembic migrations

## Package Structure

    backend/
      app/
        main.py
        config.py
        api/
          dependencies.py
          errors.py
          v1/
        schemas/
        services/
        domain/
        db/
          session.py
          models/
          queries/
        shared/
          clock.py
          identifiers.py
          exceptions.py
      tests/
        unit/
        integration/
        api/
        architecture/
        factories/

## Layer Rules

### API routes

- Parse HTTP input through Pydantic
- Resolve authentication/dependencies
- Call one application use case
- Map known exceptions to API errors
- ไม่มี SQL และ business calculations

### Application services

- Orchestrate use case
- Own transaction boundary
- Call domain rules and database queries
- Emit audit records
- Return application result ไม่คืน ORM object โดยตรง

### Domain

- Pure business rules where practical
- ไม่ import FastAPI, Starlette หรือ Vue concerns
- Clock และ random source รับจาก dependency
- Test ได้โดยไม่เปิด database

### Database

- SQLAlchemy models and focused queries
- ใช้ generic SQLAlchemy types
- ไม่มี PostgreSQL/MySQL-specific import ใน core
- Session ต่อ request/use case

### Schemas

- Request/response models แยกจาก ORM models
- Response ต้องไม่รั่ว secret, password hash หรือ is_correct
- API types มี stable names

## Dependency Injection

Dependency ที่ต้อง override ใน tests:

- get_db_session
- get_current_user
- Clock
- random generator/seed
- Settings
- CSV byte/text reader เมื่อจำเป็น

ห้ามใช้ mutable global state

## Transactions

- Service เป็นเจ้าของ commit/rollback
- Query helper ห้าม commit เอง
- Import apply เป็น transaction เดียว
- Session finalization และ scoring ต้องป้องกัน double-submit
- IntegrityError ที่คาดหมายต้องแปลงเป็น domain/API error ที่เสถียร

## Time

- ใช้ Clock abstraction
- Store UTC
- ห้ามเรียก datetime.now กระจายทั่ว codebase
- Exact boundary นิยามว่า now >= ends_at คือหมดเวลา

## Randomness

- Production ใช้ random source ที่กำหนด
- Tests inject deterministic seed
- Generated variant เก็บผลลัพธ์จริง ไม่พึ่งการสุ่มซ้ำภายหลัง

## Logging

- Structured key/value where practical
- มี request correlation ID
- ห้าม log password, token, national identifier เต็ม, answer correctness ก่อน final
- Exception ที่ทราบสาเหตุ log แบบเหมาะสม ไม่สร้าง stack trace noise

## File Size

- Hard limit 800 lines รวม blank/comment
- Soft target 150-400 lines
- แยก service ตาม use case เช่น start_exam, save_answer, submit_exam
- Architectural pytest บังคับ limit

## Dependency Rules

- Dependency pin ใน requirements.txt
- ติดตั้งผ่าน .venv เท่านั้น
- CSV ใช้ Python csv module ไม่ใช้ pandas
- TOML ใช้ pydantic-settings/tomllib ตาม implementation ที่อนุมัติ
- ห้ามเพิ่ม package หาก standard library หรือ dependency เดิมแก้ปัญหาได้ชัดเจน
