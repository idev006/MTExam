# Exam Session Requirements

## Purpose

ให้ผู้มีสิทธิ์เริ่ม ทำ และส่งข้อสอบภายในเวลาที่ server กำหนด

## Requirements

### Implemented durable exam lifecycle

- `POST /exam-sessions/windows/{window_id}/start` creates or resumes one session per person/window
- `GET /exam-sessions/{session_id}` returns questions, saved answers and server deadline
- `PUT /exam-sessions/{session_id}/answers` upserts a validated answer
- `POST /exam-sessions/{session_id}/submit` calculates and stores the immutable score
- `POST /exam-sessions/{session_id}/force-close` lets the Window owner or super admin finalize an
  in-progress session with a required audited reason
- The server finalizes an overdue in-progress session as `timed_out`; the browser clock is display-only

The current development preview is available at `/exam/pdpa`. An administrator selects the number of questions per page (1, 5, 10, 20, or 50), and the examinee can navigate directly to any page. The recovery POC creates a durable SQLite `practice_exam_sessions` row, autosaves each answer through the API, keeps a local browser recovery copy, and resumes the same session after refresh, browser restart, or temporary network loss. Score plus stored rationales are revealed only after the complete paper is submitted. Cookie-based authentication now protects the practice and settings routes; formal authenticated exam windows remain pending.

### Recovery acceptance criteria

- A session has a stable `session_id` and can be loaded again after a page reload.
- Each answer is persisted independently; retrying an answer update is safe.
- Offline or failed writes remain in browser recovery storage and are retried when the user continues or submits.
- Submit is idempotent: a repeated submit returns the existing result and never recalculates a second attempt.
- The confirmation UI reports unanswered questions; unanswered questions score zero and the server
  calculates only from immutable question/choice snapshots.

### EXAM-001 — Exam window

- Window อ้าง published paper
- กำหนด mode เป็น individual หรือ fixed_batch
- กำหนด organization scopes ได้หลายรายการ
- แต่ละ Window ต้อง snapshot quota ของตนเองจาก ExamPaper template และสามารถปรับจำนวนต่อรอบได้
- ป้องกันการเริ่มนอก window หรือ scope
- ผู้สร้างหรือ super admin เท่านั้นที่เปลี่ยน lifecycle; ทุก transition ต้องมี audit

### EXAM-002 — Individual timing

- started_at มาจาก server
- ends_at เท่ากับ started_at บวก duration
- Refresh หน้าไม่เริ่มเวลาใหม่
- `full_duration` ให้ผู้ที่เริ่มก่อนเวลาปิดรับการเริ่มสอบทำต่อจนครบ duration

### EXAM-003 — Fixed batch timing

- window_open_at และ window_close_at มาจาก server
- ends_at ของทุก session เท่ากับ window_close_at
- ผู้เข้าสายได้รับเฉพาะเวลาที่เหลือ
- Default อนุญาตเข้าสายพร้อมคำเตือน
- `fixed_end` คำนวณ `min(started_at + duration, window_close_at)`

### EXAM-003A — Operational lifecycle

- สถานะ Window คือ `scheduled`, `open`, `suspended`, `closed`, `cancelled`
- Suspended/Closed หยุด session ใหม่ แต่ไม่เปลี่ยน `ends_at` ของ session เดิม
- Closed และ Cancelled เป็น terminal state
- Suspended และ Cancelled ต้องระบุเหตุผล และ Audit ต้องเก็บเหตุผลดังกล่าว
- การเปิดรอบต้องใช้ Published ExamPaper, quota ครบ และอยู่ในช่วงเวลาที่กำหนด

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
- Force-close เรียก scoring service เดียวกันและต้องมีเหตุผลใน audit
- Response คืน maximum score, percentage, passing threshold, pass outcome และ result visibility
  เฉพาะเมื่อ policy ของ Window อนุญาต

### EXAM-009 — Recovery

- Refresh/reconnect โหลด session และคำตอบที่บันทึกแล้ว
- ไม่มี Redis requirement
- State ถาวรอยู่ใน database

### EXAM-010 — Coordinator-controlled Window scheduling

- New Exam Windows may be created only by `exam_coordinator` or `super_admin`.
- The selected Paper must be Published and have at least one exact quota bucket in coordinator scope.
- Per-Window quota may be equal to or lower than its Exam Creation template; quota escalation is rejected.
- Lifecycle mutation requires the Window creator, except audited `super_admin` override and the
  documented legacy-author transition.
- List responses expose `can_manage` so the UI does not advertise unauthorized mutations.

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
- Window quota isolation across multiple rounds
- Authorized and invalid lifecycle transitions with audit evidence
- Immediate/after-close/hidden result policy and force-close authorization
