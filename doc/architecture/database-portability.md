# Database Portability

## Supported Databases

| Database | Support profile |
|---|---|
| SQLite | Local development, tests, demo, small single-instance |
| MySQL | Production |
| PostgreSQL | Production |

Support หมายถึง application behavior และ migrations ผ่าน test matrix ไม่ได้หมายถึง performance เท่ากัน

## Connection Selection

เลือกด้วย DATABASE_URL:

    sqlite:///./data/mtexam.db
    mysql+pymysql://user:password@host/mtexam?charset=utf8mb4
    postgresql+psycopg://user:password@host/mtexam

## Allowed Portable Types

- String, Text
- Integer, Boolean
- Date, DateTime
- Numeric
- LargeBinary เมื่อจำเป็น
- ForeignKey, UniqueConstraint, Index

## Prohibited in Core

- PostgreSQL ltree, ARRAY, JSONB และ native ENUM
- PostgreSQL-only UUID type
- Partial indexes
- MySQL SET และ dialect-only types
- Stored procedures/triggers เฉพาะ engine
- Raw SQL ที่มี dialect-specific syntax
- ON CONFLICT หรือ ON DUPLICATE KEY ใน shared service

## Modeling Rules

- UUID สร้างใน application และเก็บด้วย generic Uuid หรือ String ที่อนุมัติ
- Tags ใช้ join table
- Enum ใช้ String + Python validation
- Snapshot JSON ใช้ Text และ serialize ใน application
- ข้อมูลที่ต้อง filter/report ใช้ normalized columns
- Case-insensitive identity ใช้ normalized column ไม่พึ่ง database collation
- Date/time ใช้ UTC convention

## Query Rules

- ใช้ SQLAlchemy select/insert/update/delete
- หลีกเลี่ยง database functions ที่ไม่มี equivalent
- Pagination ต้องมี deterministic order
- Upsert ทำเป็น portable service flow และ unique constraint
- Recursive organization query ต้องมี implementation/test ที่ทั้งสาม engine รองรับ หรือใช้ fixed three-level traversal

## Migration Rules

- Alembic migration ต้อง upgrade ฐานข้อมูลเปล่าได้ทุก engine
- ใช้ batch migration mode เมื่อต้องรองรับข้อจำกัด SQLite
- Migration ห้ามแก้หลัง release
- Data migration ต้อง deterministic และ restart-safe
- Release test ต้อง upgrade จาก version ก่อนหน้า

## SQLite Rules

- เปิด foreign_keys pragma ทุก connection
- ใช้ persistent file ใน production-like demo
- ห้ามใช้บน ephemeral filesystem
- ไม่รับรอง 500 concurrent writers
- หาก deploy มากกว่าหนึ่ง API instance ห้ามใช้ local SQLite file

## Test Matrix

| Test | SQLite | MySQL | PostgreSQL |
|---|---:|---:|---:|
| Unit/domain | Required | N/A | N/A |
| Migration from empty | Required | Required | Required |
| API integration | Required | Required | Required |
| Import transaction | Required | Required | Required |
| Exam answer concurrency | Basic | Required | Required |
| Unicode Thai | Required | Required | Required |

หาก CI ยังไม่พร้อมทั้งสาม engine ต้องระบุฐานข้อมูลที่ verified จริงใน status report และห้ามกล่าวว่า production-supported จนกว่าจะผ่าน
