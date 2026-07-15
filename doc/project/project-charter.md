# Project Charter

## Project

MTExam — Multiple-Choice Timed Examination System

## Sponsor/Product Owner

To be assigned

## Project Manager

To be assigned; Project Manager owns delivery tracking, cadence, risk and release readiness

## Purpose

ส่งมอบระบบสอบออนไลน์ที่เชื่อถือได้ ดูแลง่าย ใช้ infrastructure ขั้นต่ำ และสามารถเปลี่ยน UI/ฐานข้อมูลตามข้อกำหนด

## Objectives

- API-first System Core
- Personnel master import from CSV
- Individual and fixed-batch exams
- Correct randomized variants
- Immediate scoring and scoped reporting
- Auditable operations
- Portable SQLite/MySQL/PostgreSQL implementation
- Document-driven and test-friendly delivery

## Constraints

- Python ใช้ .venv ที่กำหนด
- Vite/Vue 3 Composition API frontend
- Minimal stack ไม่มี Redis initial
- Source file ไม่เกิน 800 lines
- Project status tracked in one board
- Requirement/architecture changes documented before Done

## Governance

- Product Owner อนุมัติ scope/acceptance
- Project Manager ดูแล board, readiness, WIP, blockers, risks และ release
- Technical Lead ดูแล architecture/ADR
- Developers implement พร้อม tests/docs
- Reviewer ตรวจ code, test, security และ document consistency
- Tester/acceptance owner ยืนยัน acceptance criteria

หนึ่งคนอาจทำหลาย role ในทีมขนาดเล็ก แต่ความรับผิดชอบต้องไม่หาย

## Project Tracking

Default recommendation: GitHub Issues + GitHub Projects เมื่อ repository ถูก initialize

Rules:

- No Ticket, No Development
- ทุก ticket มี owner, priority, requirement ID และ acceptance criteria
- Board เป็น SSOT ของ current status
- Repository documents เป็น SSOT ของ requirement/architecture
- Pull request เชื่อม ticket และ tests

## Success Measures

- Traceability coverage 100% สำหรับ committed release requirements
- Critical correctness/security tests ผ่าน
- Supported database matrix ผ่าน
- No source file over limit
- Release ไม่มี unresolved critical risk
- Load test ผ่าน target ที่อนุมัติก่อน production

## Initial Deliverable

Vertical slice ตั้งแต่ personnel import → auth/scope → question/paper → exam → scoring/reporting โดยแต่ละ slice deploy/test ได้
