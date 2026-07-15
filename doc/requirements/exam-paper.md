# Exam Paper and Variant Requirements

## Purpose

สร้างชุดข้อสอบจากคลังและสร้าง variant หลายชุดโดยยังคงความถูกต้องของเฉลย

## Requirements

### Exam Creation inputs

- รายการรายวิชาบนหน้า Exam Creation ต้องโหลดจาก `subjects` ผ่าน `GET /question-banks/subjects` เท่านั้น ห้าม hardcode ใน Vue
- ผู้สร้างต้องระบุจำนวนข้อที่ต้องการ (`desired_question_count`)
- ระบบต้องตรวจว่าจำนวนคำถามที่เลือกไม่น้อยกว่าจำนวนที่ต้องการ
- ผู้สร้างต้องเลือกหน่วยระดับกองบังคับการที่อนุญาตให้เข้าสอบอย่างน้อยหนึ่งหน่วย
- ระบบเก็บสิทธิ์หน่วยงานไว้กับ Exam Creation และใช้ตรวจสอบสิทธิ์ก่อนเริ่มสอบ
- UI ต้องโหลดคำถามตามรายวิชาและให้เลือกด้วย checkbox พร้อมค้นหาและตัวนับจำนวนข้อ

### PAPER-001 — Paper lifecycle

สถานะขั้นต่ำ: draft, generated, published และ archived

- Draft แก้ไขได้
- Generated มี snapshot และ variants
- Published ใช้สร้าง exam window ได้
- Published paper ห้ามแก้โครงสร้างโดยตรง
- Archived ห้ามสร้าง window ใหม่

### PAPER-002 — Fixed set

- ผู้สร้างเลือกคำถามและ score weight
- คำถามซ้ำใน paper เดียวกันไม่ได้
- Total score คำนวณจาก weight

### PAPER-003 — Random pool

- ระบุ pool criteria และจำนวนข้อ
- ระบบเลือกคำถามหนึ่งครั้งตอน generate paper
- ผลที่เลือกต้องถูกบันทึกเพื่อ reproduce
- ถ้า pool มีข้อไม่พอต้อง generate ไม่สำเร็จ

### PAPER-004 — Question version

- ตอน generate ครั้งแรกสร้าง immutable snapshot ของ content และ choices
- Variant ของ paper เดียวกันอ้าง question version ที่เลือกชุดเดียวกัน
- การแก้ต้นฉบับภายหลังไม่เปลี่ยน paper

### PAPER-005 — Variant generation

- สร้างตาม variant_count
- สุ่มลำดับคำถาม
- สุ่มลำดับตัวเลือก
- เก็บ display order เป็น stable choice IDs
- Random generator inject หรือ seed ได้สำหรับ test/reproduction

### PAPER-006 — Correctness invariant

- ทุก variant มีคำตอบถูกเดียวกันตาม choice_id
- Frontend ส่ง selected_choice_id
- Backend ไม่ตรวจจาก display index
- Automated test ต้องครอบคลุม variant จำนวนมากและทุกตำแหน่ง

### PAPER-007 — Audit

บันทึก created, edited, generated, published และ archived พร้อม actor และเวลา

## Required Tests

- Fixed/random selection
- Insufficient pool
- Snapshot immutability
- Deterministic generation ด้วย seed
- Correctness invariant
- Lifecycle transition
- Permission และ organization scope
# Exam Creation and sets

Each paper creation is an independent `Exam Creation` record (the `ExamPaper` aggregate). It
belongs to one subject and may create one or more `ExamVariant` sets. Scores, participation,
completion and averages must be grouped by this creation and never merged across creations.
