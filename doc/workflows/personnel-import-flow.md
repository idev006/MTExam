# Personnel Import Workflow

## Goal

นำ full snapshot CSV เข้าอย่างปลอดภัย ตรวจสอบได้ และไม่ทำลายประวัติ

## Main Flow

1. Import Administrator เปิดหน้าสร้าง import
2. เลือก CSV และส่ง POST /api/v1/personnel-imports
3. API ตรวจ permission, file size และ checksum
4. ระบบสร้าง batch สถานะ uploaded
5. Parse header/rows เข้า staging
6. Validate schema และข้อมูลรายแถว
7. Reconcile กับ current persons/org assignments
8. เปลี่ยน batch เป็น ready เมื่อไม่มี fatal error
9. UI แสดง preview: added, changed, moved, missing, invalid
10. หาก missing เกิน threshold แสดง safety warning
11. ผู้มีสิทธิ์ยืนยัน POST /personnel-imports/{id}/apply
12. Service re-check สถานะและ checksum
13. Apply ทุก change ใน transaction เดียว
14. เขียน audit และสรุปผล
15. Batch เป็น applied และ UI แสดงผล

## Failure Flows

### Duplicate file

- ตอบ IMPORT_DUPLICATE_FILE
- ไม่สร้างผลกระทบต่อ core data

### Invalid header

- Batch เป็น validation_failed
- รายงาน missing/unknown columns
- Apply ไม่ได้

### Invalid rows

- เก็บ row error
- Policy initial: batch ที่มี invalid identity/org reference apply ไม่ได้

### Abnormal missing

- Batch ยัง ready_with_warning
- ต้องมี override permission และ confirmation

### Apply failure

- Rollback transaction
- Batch เป็น apply_failed
- เก็บ safe error summary/correlation ID
- สามารถแก้สาเหตุและสร้าง batch ใหม่ ไม่แก้ staging แบบลับ ๆ

## State Model

    uploaded
      → validating
      → validation_failed
      → ready
      → ready_with_warning
      → applying
      → applied
      → apply_failed

## Reconciliation Table

| Current | Incoming | Action |
|---|---|---|
| absent | present | added |
| present same | present same | unchanged |
| present | changed fields | changed |
| current org A | org B | moved |
| active | absent in full snapshot | missing/inactivate |
| inactive | present | reactivate |

## Audit Events

personnel_import_uploaded, personnel_import_validated, personnel_import_applied, personnel_import_failed, personnel_import_override_confirmed

## Tests

อ้าง PER-IMP-001 ถึง PER-IMP-007 และทดสอบ transaction rollback ทุก database profile
