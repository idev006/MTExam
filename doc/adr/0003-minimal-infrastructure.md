# ADR-0003: Minimal Infrastructure

**Status:** Accepted
**Date:** 2026-07-15

## Context

โครงการอาจ deploy บน cheap/free hosting และต้องลดค่าใช้จ่าย/งาน operations

## Decision

Initial runtime มี FastAPI application และ database เท่านั้น Vue สามารถ build และ serve เป็น static files จาก application เดียว

ไม่รวม Redis, queue, PgBouncer, Kubernetes, microservices, WebSocket หรือ Nginx เป็น requirement

## Consequences

Positive:

- ติดตั้งและ debug ง่าย
- ค่าใช้จ่ายต่ำ
- Failure modes น้อย

Trade-offs:

- งานยาวต้องออกแบบไม่ block request หรือเพิ่มกลไกภายหลัง
- SQLite จำกัด concurrency

## Addition Rule

Infrastructure ใหม่ต้องมี measurement/problem statement, alternatives, operational owner และ ADR
