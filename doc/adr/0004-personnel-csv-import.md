# ADR-0004: Personnel Data by CSV Import

**Status:** Accepted
**Date:** 2026-07-15

## Context

บุคลากรและหน่วยงานมีระบบต้นทางและเปลี่ยนเป็นรอบ ทั้งเพิ่ม ลด ย้าย หรือแก้ข้อมูล MTExam ไม่ควรกลายเป็น HR master อีกชุด

## Decision

- ไม่มี manual CRUD สำหรับ person/org master
- รับ full snapshot CSV
- Stage, validate, preview และ apply transaction
- Missing person เป็น inactive ไม่ hard delete
- เก็บ assignment/history/snapshot

## Consequences

Positive:

- Ownership ชัด
- Audit/reconciliation ทำซ้ำได้
- ประวัติสอบคงอยู่

Trade-offs:

- คุณภาพระบบขึ้นกับ CSV contract
- ต้องมี safety gate เมื่อข้อมูลลดผิดปกติ

## Open

Column mapping final รอ approved sample CSV
