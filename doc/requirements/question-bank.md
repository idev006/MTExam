# Question Bank Requirements

## Purpose

จัดเก็บคำถามปรนัยที่นำไปประกอบชุดสอบได้ โดยรักษาเฉลยที่ถูกต้องและประวัติข้อสอบที่ถูกใช้งานแล้ว

## Requirements

### QBNK-001 — Bank management

- Exam Author ที่มีสิทธิ์สร้าง แก้ไข และ archive question bank
- Bank มี owner organization
- Default is_shared เป็น false
- Archived bank ห้ามนำไปสร้าง paper ใหม่

### QBNK-002 — Question management

- คำถามเป็นข้อความ
- มีตัวเลือก 4-5 ตัวเลือก
- Initial release รองรับคำตอบถูกหนึ่งตัวเลือก
- กำหนด difficulty, tags และ default score weight ได้
- ต้องมีคำตอบถูก exactly one ก่อน publish

### QBNK-003 — Choice identity

- ทุกตัวเลือกมี stable choice_id
- is_correct เป็นแหล่งความจริงเดียวของเฉลย
- ห้ามเก็บเฉลยซ้ำเป็นตัวอักษร ก ข ค ง
- การเปลี่ยน display order ไม่เปลี่ยน choice identity

### QBNK-004 — Editing

- Draft question แก้ไขได้
- การแก้ต้นฉบับไม่กระทบ question version ที่ถูก snapshot แล้ว
- ห้าม hard delete question ที่เคยถูกใช้
- ใช้ archive/status แทนการลบ

### QBNK-005 — Search

- ค้นหาด้วยข้อความ tag difficulty status และ bank
- Pagination ต้องทำที่ API
- Query ต้องใช้ SQL ที่รองรับทุกฐานข้อมูล

## Out of Scope

- รูปภาพ วิดีโอ เสียง และไฟล์แนบ
- Essay และ multiple-correct
- AI-generated questions

## Seeded Training Bank

- `data/question_banks/pdpa_50.json` contains 50 Thai multiple-choice questions for development and training verification about the Personal Data Protection Act B.E. 2562.
- Each question has a stable ID, four choices, exactly one `correct_index`, topic, and explanation.
- The bank is a development fixture; legal review is required before using it for a formal examination.

## Required Tests

- จำนวนตัวเลือกต่ำ/สูงกว่ากำหนด
- ไม่มีหรือมีหลายคำตอบถูก
- Stable choice_id
- Permission และ organization ownership
- Archived content
- Unicode และ search
