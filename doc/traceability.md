# Requirements Traceability Matrix

**Status:** Baseline; product requirements implementation not started

Test path และ ticket จะเติมเมื่อสร้าง repository/application งานจะ Done ไม่ได้หาก row ที่เกี่ยวข้องยังไม่มี evidence

| Requirement | Document | Planned API/Module | Test evidence | Status |
|---|---|---|---|---|
| DATA-EMP-001 | requirements/personnel-import.md | db.models.employee + migration 0002 | tests/integration/test_employee.py | Verified on SQLite |
| PER-IMP-001 | requirements/personnel-import.md | POST personnel-imports | TBD | Planned |
| PER-IMP-002 | requirements/personnel-import.md | import validation | TBD | Planned |
| PER-IMP-003 | requirements/personnel-import.md | import preview | TBD | Planned |
| PER-IMP-004 | requirements/personnel-import.md | POST imports/{id}/apply | TBD | Planned |
| PER-IMP-005 | requirements/personnel-import.md | reconciliation service | TBD | Planned |
| PER-IMP-006 | requirements/personnel-import.md | apply confirmation | TBD | Planned |
| PER-IMP-007 | requirements/personnel-import.md | audit module | TBD | Planned |
| AUTH-001 | requirements/authentication.md | auth sign-in | TBD | Planned |
| AUTH-002 | requirements/authentication.md | credential service | TBD | Planned |
| AUTH-003 | requirements/authentication.md | auth session | TBD | Planned |
| AUTH-004 | requirements/authentication.md | permission dependency | TBD | Planned |
| AUTH-005 | requirements/authentication.md | scope service | TBD | Planned |
| AUTH-006 | requirements/authentication.md | account lifecycle | TBD | Planned |
| QBNK-001 | requirements/question-bank.md | question-banks | TBD | Planned |
| QBNK-002 | requirements/question-bank.md | questions | TBD | Planned |
| QBNK-003 | requirements/question-bank.md | domain choice rules | TBD | Planned |
| QBNK-004 | requirements/question-bank.md | question lifecycle | TBD | Planned |
| QBNK-005 | requirements/question-bank.md | question query | TBD | Planned |
| PAPER-001 | requirements/exam-paper.md | exam-papers | TBD | Planned |
| PAPER-002 | requirements/exam-paper.md | fixed-set service | TBD | Planned |
| PAPER-003 | requirements/exam-paper.md | random-pool service | TBD | Planned |
| PAPER-004 | requirements/exam-paper.md | snapshot service | TBD | Planned |
| PAPER-005 | requirements/exam-paper.md | variant generator | TBD | Planned |
| PAPER-006 | requirements/exam-paper.md | scoring/domain invariant | TBD | Planned |
| PAPER-007 | requirements/exam-paper.md | audit module | TBD | Planned |
| EXAM-001 | requirements/exam-session.md | exam-windows | TBD | Planned |
| EXAM-002 | requirements/exam-session.md | start individual | TBD | Planned |
| EXAM-003 | requirements/exam-session.md | start fixed batch | TBD | Planned |
| EXAM-004 | requirements/exam-session.md | create session | TBD | Planned |
| EXAM-005 | requirements/exam-session.md | session read | TBD | Planned |
| EXAM-006 | requirements/exam-session.md | PUT answer | TBD | Planned |
| EXAM-007 | requirements/exam-session.md | session clock response | TBD | Planned |
| EXAM-008 | requirements/exam-session.md | submit/finalize | TBD | Planned |
| EXAM-009 | requirements/exam-session.md | session recovery | TBD | Planned |
| SCORE-001 | requirements/scoring.md | scoring domain | TBD | Planned |
| SCORE-002 | requirements/scoring.md | scoring domain | TBD | Planned |
| SCORE-003 | requirements/scoring.md | finalization service | TBD | Planned |
| SCORE-004 | requirements/scoring.md | result API | TBD | Planned |
| SCORE-005 | requirements/scoring.md | audit/results | TBD | Planned |
| REPORT-001 | requirements/reporting.md | examinee result | TBD | Planned |
| REPORT-002 | requirements/reporting.md | organization report | TBD | Planned |
| REPORT-003 | requirements/reporting.md | report summary | TBD | Planned |
| REPORT-004 | requirements/reporting.md | CSV export | TBD | Planned |
| AUDIT-001 | requirements/reporting.md | audit events | TBD | Planned |
| AUDIT-002 | requirements/reporting.md | audit schema | TBD | Planned |
| AUDIT-003 | requirements/reporting.md | audit authorization | TBD | Planned |

## Update Rules

- เมื่อสร้าง ticket ให้เพิ่ม Ticket column หรือ link ใน row ที่เกี่ยวข้อง
- เมื่อมี test ให้ใส่ exact test path/name
- Status ใช้ Planned, In Progress, Verified หรือ Deferred
- Deferred ต้องมี decision/ticket อ้างอิง
- Requirement ใหม่ต้องมี unique ID และเพิ่ม matrix
