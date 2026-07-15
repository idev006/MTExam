# ADR-0001: Modular Monolith

**Status:** Accepted
**Date:** 2026-07-15

## Context

ระบบต้องดูแลง่าย deploy ราคาต่ำ และรองรับหลาย business modules โดยยังไม่มีหลักฐานว่าต้องใช้ distributed architecture

## Decision

ใช้ Modular Monolith แยก logical modules/layers ภายใน FastAPI application เดียวและ database เดียว

## Consequences

Positive:

- Deploy และ transaction ง่าย
- Test และ refactor ได้ใน repository เดียว
- ค่า hosting ต่ำ
- ลด operational failure modes

Trade-offs:

- ต้องบังคับ module boundaries ใน code review/tests
- Scale แยก module ไม่ได้จนกว่าจะ extract service

## Revisit When

มี measured bottleneck, independent deployment need หรือ team ownership boundary ที่ monolith แก้ไม่ได้
