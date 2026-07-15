# Reporting and Audit Requirements

## Purpose

แสดงผลสอบและสถิติตามสิทธิ์ พร้อมหลักฐานการใช้งานที่ตรวจสอบย้อนหลังได้

## Requirements

### REPORT-001 — Examinee result

- ผู้เข้าสอบดู session, status, score และเวลาของตน
- ไม่เห็นข้อมูลบุคคลอื่น

### REPORT-002 — Organization report

- Admin/Viewer ดูข้อมูลตาม read scope
- รายงานใช้ org_unit snapshot ณ เวลาสอบ
- การย้ายหน่วยภายหลังไม่เปลี่ยนรายงานอดีต
- รองรับ filter window, paper, date, organization และ status

### REPORT-003 — Summary

- จำนวนผู้มีสิทธิ์ เข้าสอบ ส่งแล้ว หมดเวลา และไม่เข้าสอบ
- ค่าเฉลี่ย สูงสุด ต่ำสุด และอัตราผ่านเมื่อมี pass policy
- Aggregation ต้องให้ผลเหมือนกันบนฐานข้อมูลที่รองรับ

### REPORT-004 — Export

- Initial baseline ส่งออก CSV UTF-8
- PDF/Excel เป็น open decision และ ticket แยก
- Export ต้องเคารพ permission/filter เดียวกับหน้าจอ

### AUDIT-001 — Events

บันทึกอย่างน้อย login, import, paper lifecycle, exam start, answer create/change, submit, timeout และ admin view result

### AUDIT-002 — Audit fields

- actor_person_id เมื่อมี
- event type, subject type และ subject ID
- occurred_at UTC
- IP address และ user agent ตาม policy
- metadata ที่ไม่เก็บ secret หรือ identifier เต็ม

### AUDIT-003 — Immutability

- ผู้ใช้ทั่วไปแก้หรือลบ audit ไม่ได้
- การเข้าดู audit จำกัดสิทธิ์
- Retention policy ต้องตัดสินใจก่อน production

## Required Tests

- Scope roll-up
- Historical snapshot after transfer
- Report aggregation
- CSV Unicode
- Export permission
- Audit event coverage
- Sensitive data redaction
# Exam Creation statistics

Reports expose statistics by `Exam Creation`: subject, creation title, number of variants,
participants, submitted/in-progress counts and average score. A subject filter may narrow the
list, but statistics from different creations remain separate.
