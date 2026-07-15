# Data Model

## Conventions

- Primary key ใช้ application-generated UUID ที่เก็บแบบ portable
- Date/time เก็บ UTC
- Status/enum เก็บ String และ validate ใน application
- Foreign keys และ unique constraints บังคับ integrity
- ไม่มี hard delete สำหรับข้อมูลที่มี history
- Snapshot ที่ไม่ต้อง query ภายในเก็บ serialized JSON text

## Identity and Organization

### persons

| Column | Purpose |
|---|---|
| id | Stable internal UUID |
| identifier_encrypted | ค่าถอดกลับได้เมื่อจำเป็น |
| identifier_hash | Unique normalized lookup |
| full_name | Current name |
| rank | Current rank |
| status | active/inactive |
| status_reason | เหตุผลเมื่อ inactive |
| status_effective_date | วันที่มีผล |

### user_accounts

id, person_id, username_normalized, password_hash, role, status, must_change_password, created_at, updated_at

### org_units

id, code, name, level, parent_id, status

Unique code และ foreign key parent_id ใช้แทน ltree

### person_unit_assignments

id, person_id, org_unit_id, effective_from, effective_to

หนึ่งคนมี current assignment ได้หนึ่งรายการตาม business constraint

## Import

### personnel_import_batches

id, filename, file_checksum, import_mode, status, uploaded_by, uploaded_at, validated_at, applied_at, total_rows, valid_rows, invalid_rows, added_count, changed_count, moved_count, missing_count, error_summary_text

### personnel_import_rows

id, batch_id, row_number, raw_data_text, normalized_identifier_hash, validation_status, action, error_code, error_message

Staging row แยกจาก core person data

## Questions

### question_banks

id, name, owner_org_unit_id, is_shared, status, created_by, created_at

### questions

id, bank_id, content, difficulty, default_score_weight, status, created_at, updated_at

### question_choices

id, question_id, content, is_correct, base_order

### tags and question_tags

ใช้ normalized many-to-many แทน database array

### question_versions

id, question_id, content_snapshot, choices_snapshot_text, created_at

Snapshot immutable หลังสร้าง

## Papers and Variants

### exam_papers

id, title, question_selection_mode, pool_criteria_text, variant_count, status, org_unit_id, created_by, created_at, published_at

### exam_paper_questions

id, exam_paper_id, question_id, base_order_index, score_weight

Unique exam_paper_id + question_id

### exam_paper_selected_questions

id, exam_paper_id, question_id, score_weight

เก็บผล random pool ที่เลือกแล้ว

### exam_variants

id, exam_paper_id, variant_label, generation_seed_reference, created_at

### exam_variant_questions

id, exam_variant_id, question_version_id, order_index, choice_display_order_text, score_weight

Unique exam_variant_id + question_version_id

## Examination

### exam_windows

id, exam_paper_id, mode, duration_minutes, window_open_at, window_close_at, status, created_by

Validation:

- individual ต้องมี duration
- fixed_batch ต้องมี open/close และ close มากกว่า open

### exam_window_scopes

id, exam_window_id, org_unit_id

Unique exam_window_id + org_unit_id

### exam_sessions

id, person_id, exam_window_id, exam_variant_id, examinee_snapshot_text, org_unit_id, started_at, ends_at, submitted_at, status, score, ip_address

Unique person_id + exam_window_id ป้องกัน session ซ้ำตาม policy

### exam_answers

id, exam_session_id, exam_variant_question_id, selected_choice_id, first_answered_at, last_updated_at, is_correct_cache

Unique exam_session_id + exam_variant_question_id

is_correct_cache ไม่ใช่ SSOT

## Audit

### audit_logs

id, actor_person_id, event_type, subject_type, subject_id, occurred_at, ip_address, user_agent, metadata_text, correlation_id

## Snapshot Rules

- exam session snapshot ชื่อ ยศ และชื่อหน่วย ณ เวลาเริ่ม
- question version snapshot เนื้อหา ตัวเลือก และ is_correct ณ เวลา generate
- Snapshot ไม่ถูก update จาก master record
- Report ประวัติใช้ snapshot ไม่ใช้ชื่อหน่วยปัจจุบันแทน

## Index Baseline

- persons.identifier_hash unique
- org_units.code unique
- person_unit_assignments person_id + effective_to
- questions bank_id + status
- exam_windows status + open/close
- exam_sessions person_id + window
- exam_sessions org_unit_id + status
- exam_answers session_id + question unique
- audit_logs subject_type + subject_id + occurred_at
- import_batches checksum unique

Index จริงต้องยืนยันด้วย query/load test ไม่สร้าง index ทุก column
