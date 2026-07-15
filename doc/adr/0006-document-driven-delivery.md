# ADR-0006: Document-Driven Agile/Kanban Delivery

**Status:** Accepted  
**Date:** 2026-07-15

## Context

ต้องการให้คนและ AI coder เข้าใจ scope ตรงกัน ติดตามงานได้ และลด code/requirement drift

## Decision

- Requirement/acceptance documented ก่อน Ready
- Agile principles + Kanban board
- Project Board เป็น status SSOT
- Repository docs เป็น requirement/architecture SSOT
- ทุก ticket trace ไป test/PR/release
- Source code file hard limit 800 lines

## Consequences

Positive:

- Handoff และ review ชัด
- Tests เชื่อมกับ requirement
- Change history ตรวจสอบได้

Trade-offs:

- ต้องรักษาเอกสารและ tracker
- Definition of Done เพิ่มงาน แต่ลด rework

## Guardrail

Document-Driven ไม่ใช่ Big Design Up Front เอกสารต้องพอดีกับงานและอัปเดตแบบ incremental
