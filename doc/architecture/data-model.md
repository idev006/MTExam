# Data Model

## Conventions

- Primary key ของ core domain ใช้ application-generated UUID ที่เก็บแบบ portable
- Source-aligned master อาจใช้ stable source key เมื่อได้รับอนุมัติ; `employee.emp_cid` เป็นข้อยกเว้น
- Date/time เก็บ UTC
- Status/enum เก็บ String และ validate ใน application
- Foreign keys และ unique constraints บังคับ integrity
- ไม่มี hard delete สำหรับข้อมูลที่มี history
- Snapshot ที่ไม่ต้อง query ภายในเก็บ serialized JSON text

## Identity and Organization

### employee

Current-state personnel master ที่รับจาก CSV ใช้ชื่อ table/column ตรงกับระบบต้นทาง:

emp_cid, emp_yod, emp_fname, emp_lname, emp_position, emp_position_rank, emp_yod_rank,
emp_gender, emp_tel, emp_bh, emp_bk, emp_kk, emp_status, emp_descr, created_dt, updated_dt

- `emp_cid` เป็น String(13) primary key และเป็นข้อมูลอ่อนไหว
- rank scores เป็น nullable non-negative Integer
- `emp_tel` เป็น String ไม่ใช่ตัวเลข
- `created_dt`/`updated_dt` เก็บ naive UTC ตาม project convention
- index initial: `emp_status` และ composite organization path (`emp_bh`, `emp_bk`, `emp_kk`)
- ตารางนี้ไม่เป็น foreign key ของ exam history โดยตรง; `persons.id` ยังเป็น stable internal UUID

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

### auth_sessions

id, user_account_id, token_hash, created_at, last_seen_at, expires_at, revoked_at, revoke_reason,
ip_address, user_agent

- `token_hash` เป็น unique SHA-256 ของ opaque browser session token; raw token ไม่เก็บใน database
- index ที่ user, token hash, expiry และ revoke state รองรับการตรวจ session และจำกัดจำนวน session
- ไม่มี hard delete ระหว่าง session ที่ยังอยู่ใน audit/incident window; revoke เป็น state change

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

Question content should retain an optional `explanation`/answer rationale for learning and review screens. It must be present before a training question is published; scoring uses the stable choice identity and never derives correctness from the explanation text.

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

- employee.emp_cid primary key
- employee.emp_status
- employee emp_bh + emp_bk + emp_kk
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
