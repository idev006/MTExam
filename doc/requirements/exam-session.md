# Exam Session Requirements

## Purpose

ให้ผู้มีสิทธิ์เริ่ม ทำ และส่งข้อสอบภายในเวลาที่ server กำหนด

## Requirements

The current development preview is available at `/exam/pdpa`. It is a practice flow only: it loads the seeded PDPA bank through the API, keeps answers in client state, and reveals score plus stored rationales only after the examinee submits the complete paper. It is not yet an authenticated or durable exam session.

### EXAM-001 — Exam window

- Window อ้าง published paper
- กำหนด mode เป็น individual หรือ fixed_batch
- กำหนด organization scopes ได้หลายรายการ
- ป้องกันการเริ่มนอก window หรือ scope

### EXAM-002 — Individual timing

- started_at มาจาก server
- ends_at เท่ากับ started_at บวก duration
- Refresh หน้าไม่เริ่มเวลาใหม่

### EXAM-003 — Fixed batch timing

- window_open_at และ window_close_at มาจาก server
- ends_at ของทุก session เท่ากับ window_close_at
- ผู้เข้าสายได้รับเฉพาะเวลาที่เหลือ
- Default อนุญาตเข้าสายพร้อมคำเตือน

### EXAM-004 — Start session

- ตรวจ person active, permission, scope และ window
- คนหนึ่งมี active session ต่อ window ได้หนึ่งรายการ
- Assign variant ตามกติกาที่ reproducible/auditable
- Snapshot ชื่อ ยศ และหน่วย ณ เวลาเริ่ม

### EXAM-005 — Present questions

- API ไม่ส่ง is_correct หรือข้อมูลที่อนุมานเฉลยได้
- ส่ง choice_id และ display order
- ผู้เข้าสอบย้อนกลับแก้คำตอบได้ก่อน submit/timeout

### EXAM-006 — Save answer

- Endpoint มี semantics แบบ idempotent
- Unique ต่อ session และ variant question
- บันทึก first_answered_at และ last_updated_at
- Backend ตรวจ ownership, question membership และเวลา
- คำตอบหลังหมดเวลาไม่ถูกยอมรับ

### EXAM-007 — Countdown

- API ส่ง server_time และ ends_at
- Vue แสดง countdown โดยอิงค่าดังกล่าว
- Client clock ไม่เป็น authority
- การแก้เวลาเครื่อง client ไม่เพิ่มเวลาสอบ

### EXAM-008 — Submit and timeout

- Submit ทำครั้งเดียวแบบ transaction
- หลัง submit แก้คำตอบไม่ได้
- Request หลัง ends_at ทำให้ session เป็น timed_out ตาม use case
- Submit และ timeout เรียก scoring service เดียวกัน

### EXAM-009 — Recovery

- Refresh/reconnect โหลด session และคำตอบที่บันทึกแล้ว
- ไม่มี Redis requirement
- State ถาวรอยู่ใน database

## Required Tests

- Individual/fixed timing
- Start early/late/after close
- Duplicate start
- Scope denied
- Save/update answer
- Concurrent duplicate save
- Refresh recovery
- Boundary at exact ends_at
- Submit twice
- Client time manipulation
