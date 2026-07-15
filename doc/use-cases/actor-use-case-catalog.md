# Actor and Use-Case Catalog

**Version:** 1.0  
**Status:** Baseline  
**Date:** 2026-07-15

เอกสารนี้เป็น SSOT สำหรับ actor, สิทธิ์ และขอบเขต use case ของ MTExam โดย API เป็นจุดบังคับสิทธิ์หลัก ส่วน route guard ของ Vue เป็นเพียง UX layer

## Actors

| Actor | เป้าหมาย | ขอบเขตหลัก |
|---|---|---|
| `super_admin` | บริหารระบบและกำกับทุกโมดูล | ทุก use case, ตั้งค่า, role และ audit |
| `exam_author` | สร้าง ตรวจ และเผยแพร่เนื้อหาการสอบ | question bank, paper, preview; ไม่ทำ exam session จริง |
| `examinee` | ทำข้อสอบและติดตามผลของตนเอง | login, start/resume, answer, recovery, submit, own result |
| `viewer` | ติดตามข้อมูลแบบอ่านอย่างเดียว | dashboard, report ที่ได้รับอนุญาต; ไม่มี mutation |
| CSV source/data owner | ส่ง snapshot บุคลากร | จัดเตรียมไฟล์ CSV และยืนยัน value sets |
| Project Manager | กำกับ delivery | backlog, acceptance, risk, decision และ release evidence |

## Use Cases and Authorization

| ID | Use case | Primary actor | Allowed roles | Outcome |
|---|---|---|---|---|
| UC-AUTH-01 | Login | ทุก role | ทุก role | authenticated browser session |
| UC-AUTH-02 | Logout | ทุก role | ทุก role | session revoked and redirect to login |
| UC-ORG-01 | Import personnel CSV snapshot | Super Admin | `super_admin` | validated employee current-state |
| UC-SUBJECT-01 | Manage/select subject | Exam Author | `exam_author`, `super_admin`, `viewer` (read) | subject-bound content |
| UC-ADMIN-01 | Manage system settings | Super Admin | `super_admin` | typed settings persisted and audited |
| UC-QBANK-01 | Author question bank | Exam Author | `exam_author`, `super_admin` | versioned question bank |
| UC-QBANK-02 | Manage questions and choices in bank | Exam Author | `exam_author`, `super_admin` | validated draft questions and published bank |
| UC-PAPER-01 | Create and publish exam paper | Exam Author | `exam_author`, `super_admin` | published paper/variant |
| UC-PAPER-02 | Create Exam Creation and sets | Exam Author | `exam_author`, `super_admin` | independent subject-bound creation and variants |
| UC-EXAM-01 | Start or resume exam | Examinee | `examinee`, controlled `super_admin` preview | durable exam session |
| UC-EXAM-02 | Answer and autosave | Examinee | `examinee`, controlled `super_admin` preview | server/local recovery state |
| UC-EXAM-03 | Submit exam | Examinee | `examinee`, controlled `super_admin` preview | immutable score/result |
| UC-REPORT-01 | View report | Viewer | `viewer`, `super_admin` | read-only report within scope |
| UC-REPORT-02 | View Exam Creation statistics | Viewer | `viewer`, `super_admin`, `exam_author` | statistics never merged across creations |

## Cross-cutting rules

- Authentication is required for all use cases except public health/config endpoints.
- Authorization is enforced at API/service boundaries; hiding a button is not security.
- `viewer` cannot call mutation endpoints.
- Score and rationales are unavailable until `UC-EXAM-03` completes.
- Exam answers are durable, retryable, and resumable after refresh, restart, or temporary network loss.
- Every mutation that affects people, access, exam content, or result must create an audit event.

Detailed sequence diagrams are in [use-case-sequence-diagrams.md](../workflows/use-case-sequence-diagrams.md).
