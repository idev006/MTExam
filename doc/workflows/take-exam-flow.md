# Take Exam Workflow

## Preconditions

- Person และ account active
- Window open/eligible
- Person organization อยู่ใน scope
- Paper published

## Start

1. Examinee เปิดรายการรอบสอบ
2. Vue เรียก GET /exam-windows/eligible
3. ผู้ใช้เลือกเริ่ม POST /exam-windows/{id}/sessions
4. Backend ตรวจ auth, scope, window และ duplicate session
5. Assign variant
6. Snapshot examinee
7. กำหนด started_at และ ends_at จาก server
8. Commit session
9. Response ส่ง session, server_time, ends_at, questions และ choices โดยไม่มีเฉลย

## Answer

1. ผู้ใช้เลือก choice
2. Vue อัปเดต local/session view
3. PUT /exam-sessions/{session}/answers/{question}
4. Backend ตรวจ ownership, session status, membership และ time
5. Insert หรือ update answer
6. Response ส่ง saved_at และ selected_choice_id

ผู้ใช้ย้อนกลับแก้ได้ตราบใดที่ session in_progress และยังไม่หมดเวลา

## Refresh/Reconnect

1. Vue โหลด GET /exam-sessions/{id}
2. Backend ส่ง stored answers และ current server_time
3. UI rebuild countdown จาก ends_at
4. ไม่สร้าง session หรือเวลาใหม่

## Submit

1. User confirms submit
2. POST /exam-sessions/{id}/submit
3. Backend lock/check final state และ time
4. หากยังทัน: status submitted
5. หากหมด: status timed_out
6. Scoring service คำนวณจาก choice IDs/snapshot
7. Commit final status, score และ audit
8. ส่ง result ตาม visibility policy

## Boundary Rules

- now < ends_at: save/normal submit ได้
- now >= ends_at: save ไม่ได้และ finalization เป็น timed_out
- Duplicate submit คืน final result เดิมหรือ conflict ตาม API contract แต่ห้ามคิดคะแนนซ้ำผิดผล

## Client Failure

- คำตอบที่ยังไม่ commit อาจสูญหาย จึง save เมื่อเลือก/เปลี่ยนข้อแบบ debounce ที่เหมาะสม
- Server state เป็น SSOT
- ไม่มี browser local storage เป็นแหล่งความจริง

## Audit Events

exam_start, answer_create, answer_change, exam_submit, exam_timeout, result_view

## Tests

อ้าง EXAM-001 ถึง EXAM-009 และ SCORE-001 ถึง SCORE-005
