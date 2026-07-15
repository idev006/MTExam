# Personnel and Organization Import Requirements

**Owner:** Product Owner / Project Manager
**Status:** Employee column contract approved; representative CSV values pending sample file

## Purpose

นำข้อมูลบุคลากรและโครงสร้างหน่วยงานจากระบบต้นทางเข้าสู่ MTExam เป็นรอบ โดยไม่มีหน้าจอแก้ไข master data บุคลากรโดยตรง

## Actors

- Import Administrator
- System Administrator
- Auditor

## Preconditions

- ผู้ใช้งานผ่าน authentication และมี permission นำเข้า
- ไฟล์เป็น CSV ตาม column contract ที่อนุมัติ
- ไม่มี import batch อื่นกำลัง apply

## Requirements

### DATA-EMP-001 — Employee current-state master

ระบบต้องมีตาราง `employee` สำหรับ current state ที่มาจากข้อมูลต้นทาง โดยไม่มีหน้าจอ CRUD
แก้ไข master data ด้วยมือ

Acceptance criteria:

- AC01 ตารางชื่อ `employee` และมี column ตาม Employee Table Contract
- AC02 `emp_cid` เป็น primary key แบบ String(13) และห้ามซ้ำ
- AC03 `emp_position_rank` และ `emp_yod_rank` เป็น integer ที่ไม่ติดลบเมื่อมีค่า
- AC04 `emp_tel` เป็น string เพื่อรักษาเลขศูนย์นำหน้า
- AC05 `created_dt` และ `updated_dt` เป็น UTC timestamp ที่ระบบจัดการ
- AC06 ใช้ SQLAlchemy/Alembic type ที่รองรับ SQLite, MySQL และ PostgreSQL
- AC07 ไม่มี API สำหรับแก้ employee โดยตรง

### PER-IMP-001 — Upload and stage

ระบบต้องรับ CSV บันทึก import batch และ parse ทุกแถวเข้า staging ก่อนแก้ข้อมูลจริง

Acceptance criteria:

- AC01 ปฏิเสธไฟล์ที่เกินขนาด configuration
- AC02 รองรับ UTF-8 และ UTF-8 with BOM
- AC03 เก็บชื่อไฟล์ checksum ผู้นำเข้า เวลา และจำนวนแถว
- AC04 ไฟล์ checksum เดิมต้องไม่ถูก apply ซ้ำ
- AC05 ข้อมูลจริงไม่เปลี่ยนระหว่าง staging

### PER-IMP-002 — Validate

ระบบต้องตรวจ header, required field, data type, duplicate identifier และ organization reference

Acceptance criteria:

- AC01 แสดง error ระดับแถวพร้อม code และ column
- AC02 แถวผิดไม่ถูกซ่อนหรือข้ามโดยไม่มีรายงาน
- AC03 batch ที่มี fatal schema error ไม่สามารถ preview/apply
- AC04 validation สามารถรันซ้ำและให้ผลเดิม

### PER-IMP-003 — Reconcile

ระบบต้องเปรียบเทียบ staging กับ current data และจำแนก added, unchanged, changed, moved, missing และ invalid

Acceptance criteria:

- AC01 บุคคลใหม่ถูกระบุเป็น added
- AC02 การเปลี่ยนชื่อ/ยศถูกระบุเป็น changed
- AC03 การเปลี่ยนหน่วยถูกระบุเป็น moved
- AC04 บุคคลที่ไม่อยู่ใน full snapshot ถูกระบุเป็น missing
- AC05 preview แสดงยอดรวมและรายละเอียดก่อน apply

### PER-IMP-004 — Apply transaction

การ apply ต้องทำใน database transaction เดียว

Acceptance criteria:

- AC01 หากขั้นตอนใดล้มเหลวข้อมูลทั้ง batch rollback
- AC02 คนใหม่สร้าง person และ current assignment
- AC03 คนย้ายหน่วยปิด assignment เดิมและสร้างรายการใหม่
- AC04 missing เปลี่ยนเป็น inactive และปิด current assignment
- AC05 ห้าม hard delete person, assignment และ exam history
- AC06 batch ที่ apply แล้ว apply ซ้ำไม่ได้

### PER-IMP-005 — Reappearance

บุคคล inactive ที่กลับมาในรอบใหม่ต้องใช้ identity เดิม

Acceptance criteria:

- AC01 person_id เดิมไม่เปลี่ยน
- AC02 status กลับเป็น active
- AC03 สร้าง assignment ใหม่โดยไม่แก้ประวัติเก่า

### PER-IMP-006 — Safety gate

ระบบต้องหยุดการ apply ที่มีความเสี่ยงผิดปกติ

Acceptance criteria:

- AC01 หาก missing percent เกิน configuration ต้องยืนยันเพิ่ม
- AC02 แสดงยอดก่อน/หลังและผลกระทบ
- AC03 ผู้ไม่มี permission override ไม่สามารถ apply

### PER-IMP-007 — Audit

ทุก batch ต้องตรวจสอบย้อนหลังได้

Acceptance criteria:

- AC01 เก็บ actor, timestamp, IP, checksum และผลลัพธ์
- AC02 เก็บ row errors และ reconciliation summary
- AC03 audit ไม่เปิดเผย identifier เต็มใน log

## Employee Table Contract

| Column | Type | Required | Description |
|---|---|---:|---|
| emp_cid | String(13), PK | Yes | เลขประจำตัวประชาชนและ stable source identifier |
| emp_yod | String(100) | No | ยศ |
| emp_fname | String(150) | Yes | ชื่อ |
| emp_lname | String(150) | Yes | นามสกุล |
| emp_position | String(255) | No | ตำแหน่ง |
| emp_position_rank | Integer >= 0 | No | คะแนนระดับตำแหน่ง |
| emp_yod_rank | Integer >= 0 | No | คะแนนระดับชั้นยศ |
| emp_gender | String(20) | No | เพศ; รอชุดค่าจริงจาก sample |
| emp_tel | String(20) | No | หมายเลขมือถือ |
| emp_bh | String(255) | No | กองบัญชาการ |
| emp_bk | String(255) | No | กองบังคับการ |
| emp_kk | String(255) | No | กองกำกับการ |
| emp_status | String(30) | Yes | สถานะ; default `active` |
| emp_descr | Text | No | หมายเหตุ |
| created_dt | DateTime UTC | System | วันที่สร้างรายการ |
| updated_dt | DateTime UTC | System | วันที่ปรับปรุงรายการ |

## CSV Contract

- Header SSOT อยู่ใน `[personnel_import.columns]` ของ `config/app.toml`
- CSV initial ต้องมี `emp_cid`, `emp_fname`, `emp_lname` และ `emp_status`
- `created_dt` และ `updated_dt` ไม่ใช่ input ที่บังคับ; ระบบเป็นผู้สร้าง/ปรับปรุง
- Sample CSV ยังจำเป็นเพื่อยืนยัน encoding, รูปแบบเบอร์โทร และชุดค่าของ `emp_gender`/`emp_status`

## Business Rules

- Initial release ใช้ full snapshot เป็น default
- Delta import ยังไม่อยู่ใน initial scope
- Identifier ต้อง normalize ก่อน hash และ match
- ค่า sensitive ห้ามเขียนลง application log
- `emp_cid` เป็นข้อมูลอ่อนไหว ต้อง mask ใน UI/log และจำกัดสิทธิ์ไฟล์ SQLite
- ไม่มี API สำหรับแก้ person โดยตรง

## Out of Scope

- HR workflow
- อนุมัติการย้ายหน่วย
- Payroll
- การแก้ข้อมูลต้นทาง

## Required Tests

- New, changed, moved, missing และ reappeared
- Duplicate file และ duplicate row
- Invalid header และ invalid organization
- Transaction rollback
- Missing threshold safety gate
- Unicode ภาษาไทย
- ประวัติ exam session ไม่เปลี่ยนหลัง import
## ภ.6 organization seed

Development/test environments include the ภ.6 division and its 13 bureau-level child units
from the approved list. The seed is idempotent and uses stable codes; production data remains
managed through the CSV import workflow.
