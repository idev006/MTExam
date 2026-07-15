# ADR-0002: API as System Core

**Status:** Accepted  
**Date:** 2026-07-15

## Context

ต้องการเปลี่ยน UI ในอนาคตและไม่ให้ business rules กระจายระหว่าง Vue กับ Backend

## Decision

FastAPI REST API เป็น System Core และ enforcement point ของ validation, authorization, timing, scoring และ lifecycle ส่วน Vue เป็น presentation tier

## Consequences

Positive:

- เปลี่ยน UI/เพิ่ม client ได้
- pytest ครอบคลุม core rules
- Security boundary ชัด

Trade-offs:

- API contract ต้องจัดการอย่างมีวินัย
- UI ต้อง handle network/loading/error

## Rules

- Frontend ห้ามเข้าฐานข้อมูล
- Client validation ไม่แทน server validation
- OpenAPI เป็น executable API schema
