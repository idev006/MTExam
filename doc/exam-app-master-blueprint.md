# MTExam Master Blueprint

## ระบบสอบออนไลน์แบบเลือกตอบและจับเวลา

**Version:** 4.0
**Status:** Approved baseline
**Updated:** 2026-07-15
**Owner:** Project Manager

เอกสารนี้เป็นภาพรวมระดับสูงของโครงการ รายละเอียดเชิง requirement, architecture, workflow และการส่งมอบอยู่ในเอกสารที่เชื่อมจาก [Document Index](index.md)

## 1. Product Vision

MTExam คือระบบสอบออนไลน์แบบปรนัยสำหรับองค์กรตำรวจ รองรับโครงสร้างหน่วยงาน 3 ระดับ การสร้างคลังข้อสอบ การสร้างชุดสอบหลาย variant การจัดรอบสอบรายบุคคลและพร้อมกัน การบันทึกคำตอบ การตรวจคะแนนทันที การรายงานผลตามขอบเขตสิทธิ์ และ audit log

ระบบบุคลากรของ MTExam ไม่ใช่ระบบ HR และไม่มีหน้าจอ CRUD บุคลากร ข้อมูลบุคลากรและหน่วยงานมาจาก CSV ที่นำเข้าเป็นรอบ ระบบทำหน้าที่ตรวจสอบ กระทบยอด เก็บประวัติ และคงประวัติการสอบเท่านั้น

## 2. Product Goals

- API เป็น System Core และเป็นเจ้าของ business rules ทั้งหมด
- เปลี่ยนหรือเพิ่ม UI ได้โดยไม่แก้ business logic และฐานข้อมูล
- รองรับ Vue 3 SPA และเปิดทางสำหรับ mobile หรือ UI อื่นในอนาคต
- เริ่มด้วยเทคโนโลยีขั้นต่ำและเพิ่ม infrastructure เมื่อมีหลักฐานจากการทดสอบ
- สลับฐานข้อมูลระหว่าง SQLite, MySQL และ PostgreSQL ได้ผ่าน configuration
- รองรับการสอบแบบ individual และ fixed batch
- รองรับเป้าหมาย 500 concurrent users เมื่อใช้ฐานข้อมูล production ที่เหมาะสม
- รักษาประวัติบุคคล หน่วยงาน ข้อสอบ และผลสอบอย่างตรวจสอบย้อนหลังได้
- พัฒนาแบบ Document-Driven, Agile/Kanban และ pytest-friendly

## 3. Scope

### In scope

- Authentication และ role-based authorization
- การนำเข้าบุคลากรและโครงสร้างหน่วยงานจาก CSV
- Full snapshot import และการกระทบยอดข้อมูล
- ประวัติการสังกัดและ soft deactivation
- Question bank และคำถามข้อความ 4-5 ตัวเลือก
- ชุดข้อสอบแบบ fixed set และ random pool
- การสร้าง variant โดยสุ่มลำดับข้อและตัวเลือก
- รอบสอบแบบ individual และ fixed batch
- Server-authoritative timer
- บันทึกและแก้ไขคำตอบก่อนหมดเวลา
- ตรวจคะแนนและแสดงผลทันที
- รายงานตามขอบเขตหน่วยงาน
- Audit log

### Out of scope for initial release

- ระบบ HR หรือหน้าจอแก้ไข master data บุคลากร
- Proctoring, lockdown browser, webcam monitoring
- รูปภาพ วิดีโอ หรือไฟล์แนบในคำถาม
- Mobile application
- Microservices
- Redis, message queue และ distributed cache
- Data warehouse และ advanced analytics
- Exclusion หน่วยลูกจาก scope จนกว่าจะมี use case ที่อนุมัติ

## 4. Users and Roles

| Role | Read scope | Write scope |
|---|---|---|
| Super Admin | ทั้งระบบ | ตั้งค่าระบบและบัญชีผู้ใช้ |
| Division Admin | หน่วยตนเองและหน่วยลูก | งานสอบตามสิทธิ์ที่ได้รับ |
| Bureau Admin | หน่วยตนเองและหน่วยลูก | งานสอบในสังกัด |
| Station Admin | หน่วยตนเอง | จัดสอบและดูผลในหน่วย |
| Exam Author | คลังที่ได้รับสิทธิ์ | สร้างและแก้ไขข้อสอบ |
| Exam Coordinator | Published Exam Creation และรอบสอบตามหน่วยงานที่ได้รับมอบหมาย | สร้างและควบคุม Exam Window ภายใน quota template |
| Examinee | ข้อมูลตนเอง | ทำข้อสอบและดูผล |
| Viewer | ตาม scope | อ่านรายงานเท่านั้น |

โครงสร้างหน่วยงาน:

    Division
      └─ Bureau
          ├─ Station
          └─ Sub-unit / ฝ่าย / กลุ่มงาน

ใช้ parent_id แบบ portable ไม่ใช้ PostgreSQL ltree

ข้อมูลอ้างอิงตำรวจภูธรภาค 6 ใช้ `doc/p6-station.txt` เป็น checked-in source สำหรับ development
และ test seed โดยหน่วยระดับปฏิบัติการต้องผูกกับ parent ที่ระบุในเอกสาร เช่น ฝ่ายอำนวยการ 1–6
อยู่ใต้ บก.อก.ภ.6, หน่วยสืบสวน/วิเคราะห์ข่าว/ปพ./กลุ่มงานสอบสวนอยู่ใต้ บก.สส.ภ.6 และ 4 ฝ่าย/กลุ่ม
อยู่ใต้ ศฝร.ภ.6

## 5. System Architecture

MTExam เป็น Modular Monolith แบบ Multi-tier:

    Browser
      ↓
    Vite + Vue 3 SPA
      ↓ REST /api/v1
    FastAPI Application
      ├─ API routes
      ├─ Application services
      ├─ Pure domain rules
      └─ SQLAlchemy data access
      ↓
    SQLite | MySQL | PostgreSQL

Dependency direction:

    Presentation → API → Application Service → Domain/Data

Frontend ห้ามเข้าถึงฐานข้อมูลโดยตรง และห้ามเป็นผู้ตัดสินสิทธิ์ เวลา คะแนน หรือสถานะสอบ

## 6. Minimal Technology Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic v2 และ pydantic-settings
- SQLAlchemy 2 แบบ synchronous
- Alembic
- pytest, pytest-cov และ HTTPX
- Ruff
- Python virtual environment ที่ F:\programming\python\MTExam\.venv

### Frontend

- Vite
- Vue 3 Composition API
- TypeScript
- Vue Router
- Pinia เฉพาะ global state ที่จำเป็น
- Tailwind CSS
- daisyUI

### Data

- SQLite สำหรับ local development, automated tests และ demo ขนาดเล็ก
- MySQL หรือ PostgreSQL สำหรับ production
- ห้ามใช้ database-specific feature ใน core schema และ queries

### Not included initially

- Redis
- Celery หรือ message broker
- PgBouncer
- WebSocket
- Nginx เป็น requirement
- Kubernetes

## 7. Personnel Import Model

ทุก import เป็น batch ที่ตรวจสอบย้อนหลังได้:

    Upload CSV
      → Parse to staging
      → Validate
      → Reconcile
      → Preview added/changed/moved/missing/invalid
      → Confirm
      → Apply in one transaction
      → Audit result

กฎสำคัญ:

- Match บุคคลด้วย identifier ที่เสถียรและเก็บ hash สำหรับ lookup
- คนใหม่สร้าง person และ assignment
- ข้อมูลเปลี่ยนอัปเดต current record พร้อม audit
- ย้ายหน่วยปิด assignment เดิมและสร้าง assignment ใหม่
- คนที่หายจาก full snapshot เปลี่ยนเป็น inactive ห้าม hard delete
- คนที่กลับมาเปลี่ยนเป็น active และเปิด assignment ใหม่
- ไฟล์ซ้ำตรวจด้วย checksum
- การลดลงผิดปกติต้องหยุดเพื่อให้ผู้มีสิทธิ์ยืนยัน
- ประวัติ exam session ใช้ snapshot ณ เวลาสอบและไม่เปลี่ยนตามข้อมูลรอบใหม่

## 8. Exam Model

### Exam paper

- fixed_set: ผู้สร้างเลือกคำถามแน่นอน
- random_pool: ระบบเลือกจาก pool หนึ่งครั้งต่อ paper
- variant_count กำหนดจำนวนชุด A/B/C/D

### Question snapshot

เมื่อ generate variant ครั้งแรก ระบบสร้าง question version เพื่อ snapshot เนื้อหา ตัวเลือก และเฉลย ข้อสอบที่เผยแพร่แล้วไม่เปลี่ยนตามการแก้ไขต้นฉบับภายหลัง

### Correctness invariant

- question choice ID เป็น identity ของคำตอบ
- is_correct มีแหล่งความจริงเดียว
- Frontend ส่ง choice_id ไม่ส่งตัวอักษรหรือตำแหน่ง
- การสลับลำดับตัวเลือกต้องไม่เปลี่ยนเฉลย
- ต้องมี automated tests ยืนยัน invariant นี้

### Exam window

- individual: ends_at = started_at + duration
- fixed_batch: ends_at = window_close_at
- เวลา server เป็นแหล่งความจริง
- Client countdown มีหน้าที่แสดงผลเท่านั้น
- แต่ละ Window snapshot quota, completion policy และ result visibility (`immediate`,
  `after_window_close`, `hidden`) แยกจาก ExamPaper
- Submit, timeout และ force-close ต้องใช้ scoring finalization path เดียวกันและสร้าง audit event

### Answer saving

- ใช้ composite unique constraint ต่อ session และ question
- การบันทึกซ้ำต้องให้ผลเหมือนเดิม
- Backend ตรวจเวลาทุกครั้ง
- ไม่ใช้ Redis TTL

## 9. Configuration SSOT

- config/app.toml เป็น SSOT ของ non-secret runtime configuration
- Environment variables เก็บ secret และ database URL
- PostgreSQL, MySQL และ SQLite เลือกผ่าน DATABASE_URL
- Frontend รับเฉพาะ public configuration ผ่าน API
- requirements.txt เป็นรายการ Python dependencies ที่ pin version
- package-lock.json เป็น dependency lock ของ Frontend

## 10. Quality Architecture

- Business rules สำคัญเขียนเป็น pure functions
- Clock และ random generator inject ได้เพื่อทดสอบแบบ deterministic
- API, schemas, services, domain และ database แยกความรับผิดชอบ
- Source code file ทุกไฟล์ต้องไม่เกิน 800 บรรทัด
- เป้าหมายปกติ 150-400 บรรทัด และพิจารณาแยกเมื่อเกิน 500-600
- pytest architectural test ต้องตรวจ file-size limit
- Integration tests ต้องใช้ database จริงตาม support matrix
- ไม่มี feature ใด Done ถ้าเอกสารและ tests ไม่ตรงกับ implementation

## 11. Delivery Model

ใช้ Agile principles และ Kanban:

    Backlog → Analysis → Ready → In Progress → Review → Verify → Done

กติกา:

- No Ticket, No Development
- No Requirement, Not Ready
- No Test, Not Done
- No Tracker Update, Work Not Complete
- Project Board เป็น SSOT ของสถานะงาน
- เอกสารใน repository เป็น SSOT ของ requirement และ architecture
- ทุก ticket เชื่อม Requirement ID, test, pull request และ release

## 12. Delivery Phases

### Phase 0 — Foundation

- Project structure, configuration, logging และ database connection
- Architectural tests และ pytest setup
- Initial migrations
- Authentication baseline

### Phase 1 — Personnel and organization

- CSV staging, validation, preview และ apply
- Organization hierarchy
- Assignment history
- Role and scope checks

### Phase 2 — Question and paper

- Question bank
- Fixed set และ random pool
- Question version snapshot
- Variant generation

### Phase 3 — Examination

- Exam window และ scope
- Session start
- Timer และ answer saving
- Submit, timeout และ scoring

### Phase 4 — Reporting and hardening

- Result dashboards
- Audit log
- Database portability test matrix
- Load testing
- Accessibility และ operational documentation

## 13. Open Decisions

| ID | Decision | Default until approved |
|---|---|---|
| OD-001 | ใช้ local account หรือเชื่อม SSO | Local account baseline |
| OD-002 | Shared question bank ข้ามหน่วย | is_shared = false |
| OD-003 | ผู้เข้าสอบ fixed batch ที่เหลือเวลาน้อยมาก | อนุญาตพร้อมคำเตือน |
| OD-004 | รูปแบบ export รายงาน | CSV ก่อน PDF/Excel |
| OD-005 | Full snapshot column contract จากระบบต้นทาง | รอ sample CSV ที่อนุมัติ |

## 14. Success Criteria

- Import รอบใหม่ไม่ทำลายประวัติบุคลากรหรือผลสอบ
- Variant ทุกชุดตรวจเฉลยเดียวกันอย่างถูกต้อง
- การเปลี่ยน UI ไม่กระทบ business logic
- Test suite ผ่านบนฐานข้อมูลที่ประกาศรองรับ
- ระบบ deploy แบบ single application ได้
- ไม่มี source file เกิน 800 บรรทัด
- Requirement ทุกข้อ trace ไปยัง test และ delivery item ได้
- Load test ยืนยันเป้าหมายที่ตกลงก่อน production

## 15. Authority and Change Control

หากเอกสารขัดกัน ให้ใช้ลำดับ:

1. Approved requirement และ decision register
2. Master blueprint
3. ADR
4. Architecture และ workflow documents
5. Code comments

การเปลี่ยน scope, security, data ownership, database portability หรือ runtime architecture ต้องสร้าง ticket อัปเดตเอกสาร และบันทึก decision ก่อน implement
