# Scoring Requirements

## Purpose

ตรวจคะแนนอย่างถูกต้อง ทำซ้ำได้ และไม่ขึ้นกับลำดับการแสดงตัวเลือก

## Requirements

### SCORE-001 — Source of truth

- ตรวจ selected_choice_id กับ snapshot choice ที่ is_correct
- ห้ามตรวจจากตัวอักษรหรือ index
- score weight มาจาก exam_variant_question

### SCORE-002 — Calculation

- คำตอบถูกได้ score weight
- คำตอบผิดหรือไม่ตอบได้ศูนย์ใน initial release
- total score เป็นผลรวมรายข้อ
- ใช้ Numeric/Decimal เมื่อมีคะแนนทศนิยม

### SCORE-003 — Invocation

- ตรวจเมื่อ submitted หรือ timed_out
- การเรียกซ้ำต้องให้ผลเดิม
- Scoring อยู่ใน transaction เดียวกับ finalization ที่เหมาะสม

### SCORE-004 — Result visibility

- Exam Window กำหนด `immediate`, `after_window_close` หรือ `hidden`
- ค่าเริ่มต้น `immediate` รักษา compatibility กับรอบเดิม
- ผู้ดูแลดูตาม organization scope
- API ไม่เปิดเผยเฉลยก่อน session final
- เมื่อ policy ยังไม่อนุญาต API ต้องซ่อน score, maximum score, percentage, pass state และ rationale

### SCORE-005 — Audit

- เก็บ final score, submitted_at/status และ audit event สำหรับ submit, timeout และ force-close
- การแก้คะแนนโดย admin ไม่อยู่ใน initial scope

## Required Tests

- Correct, incorrect และ unanswered
- Decimal weights
- ทุก variant display order
- Duplicate scoring
- Timeout scoring
- Result permission
- No answer leakage before finalization
