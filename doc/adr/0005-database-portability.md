# ADR-0005: SQLite, MySQL and PostgreSQL Portability

**Status:** Accepted
**Date:** 2026-07-15

## Context

Hosting อาจเปลี่ยนและต้องเลือก database ตามงบประมาณ โดยไม่ rewrite application

## Decision

รองรับ SQLite, MySQL และ PostgreSQL ผ่าน SQLAlchemy/Alembic และใช้ portable subset

ห้าม ltree, ARRAY, JSONB, native ENUM, dialect upsert และ raw dialect SQL ใน core

## Consequences

Positive:

- Local setup ง่าย
- เปลี่ยน production provider ได้
- ลด vendor lock-in

Trade-offs:

- ไม่ใช้ optimization/features เฉพาะ engine
- ต้องรัน test matrix และเขียน migrations ระมัดระวัง
- SQLite ไม่รองรับ production workload เท่าฐานข้อมูล server

## Support Rule

Database ถูกประกาศ production-supported เมื่อ migrations และ integration suite ผ่าน engine/version นั้น
