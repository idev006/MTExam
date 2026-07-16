# Requirements Traceability Matrix

**Status:** Updated 2026-07-15; MVP vertical slices implemented, production hardening remains

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
| AUTH-003 | requirements/authentication.md | auth session policy + auth_sessions | tests/integration/test_auth_sessions.py | Implemented baseline |
| ADMIN-001 | requirements/administration-settings.md | settings view + future settings API | frontend type-check/build; API tests pending | POC implemented |
| ADMIN-002 | requirements/administration-settings.md | theme store and daisyUI selector | frontend architecture test | Implemented client baseline |
| EXAM-POC-001 | requirements/exam-session.md, requirements/question-bank.md | practice bank API + examinee practice view | tests/api/test_system_api.py; browser smoke verification | POC implemented |
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
| REPORT-001 | requirements/reporting.md | reports/my-results + people detail | tests/api/test_reporting_api.py | Verified automated |
| REPORT-002 | requirements/reporting.md | reports/dashboard scoped organization aggregation | tests/api/test_reporting_api.py | Verified automated |
| REPORT-003 | requirements/reporting.md | Exam Creation KPI/chart aggregation | tests/unit/test_report_rules.py; tests/api/test_reporting_api.py | Verified automated |
| REPORT-004 | requirements/reporting.md | shared-filter PDF/XLSX/CSV export | tests/api/test_reporting_api.py; frontend reporting tests | Verified automated |
| REPORT-005 | requirements/reporting.md | pass policy and quota enforcement | report rules tests; migration drift test | Verify; PostgreSQL concurrency acceptance pending |
| AUDIT-001 | requirements/reporting.md | audit events | TBD | Planned |
| AUDIT-002 | requirements/reporting.md | audit schema | TBD | Planned |
| AUDIT-003 | requirements/reporting.md | audit authorization | TBD | Planned |
| PER-IMP-API | requirements/personnel-import.md | GET/POST personnel snapshot API | API smoke test | Implemented minimal slice |
| REPORT-API | requirements/reporting.md | GET reports/summary | API smoke test | Implemented minimal slice |
| QBANK-API | requirements/question-bank.md | question-banks authoring API | API authorization smoke | Implemented minimal slice |
| PAPER-API | requirements/exam-paper.md | exam paper list/create/publish API | API authorization smoke | Implemented minimal slice |
| USER-ADMIN-API | requirements/authentication.md | user list/create/deactivate API | API authorization smoke | Implemented minimal slice |
| EXAM-WINDOW-API | requirements/exam-session.md | exam window list/create/open API | API authorization smoke | Implemented minimal slice; timer integration pending |
| AUDIT-API | requirements/reporting.md | audit list and mutation events | API authorization smoke | Implemented baseline; full mutation coverage pending |
| SUBJECT-001 | requirements/question-bank.md | subjects and subject-bound question banks | API/frontend build | Implemented |
| QBANK-UI-001 | requirements/question-bank.md | bank/question management UI | Vue type-check/build; API smoke | Implemented MVP |
| EXAM-CREATION-STATS-001 | requirements/exam-paper.md, requirements/reporting.md | per-paper Exam Creation statistics | API/frontend build | Implemented baseline |
| PAPER-SCOPE-001 | requirements/exam-paper.md | desired question count and allowed bureau units | API/frontend build | Implemented |
| EXAM-SESSION-API-001 | requirements/exam-session.md | start/resume, answer, timeout and submit endpoints | tests/api/test_system_api.py; API smoke | Implemented |
| USECASE-SEQ-COVERAGE-001 | use-cases/actor-use-case-catalog.md | sequence diagram for every catalog use case | tests/architecture/test_document_traceability.py | Verified |

## Use-case interaction traceability

| Use-case set | Catalog | Sequence evidence | Implementation/test link |
|---|---|---|---|
| Authentication and RBAC | use-cases/actor-use-case-catalog.md | workflows/use-case-sequence-diagrams.md — UC-AUTH-01/02 | backend/app/api/v1/auth.py; tests/api/test_system_api.py |
| Personnel import | use-cases/actor-use-case-catalog.md | workflows/use-case-sequence-diagrams.md — UC-ORG-01 | requirements/personnel-import.md; domain import POC |
| Question/paper authoring | use-cases/actor-use-case-catalog.md | workflows/use-case-sequence-diagrams.md — UC-QBANK-01/UC-PAPER-01 | requirements/question-bank.md, exam-paper.md |
| Durable examination | use-cases/actor-use-case-catalog.md | workflows/use-case-sequence-diagrams.md — UC-EXAM-01/02/03 | backend/app/api/v1/practice_exam.py; tests/api/test_system_api.py |
| Reporting | use-cases/actor-use-case-catalog.md | workflows/use-case-sequence-diagrams.md — UC-REPORT-01/02/03/04 | backend/app/services/reporting.py; tests/api/test_reporting_api.py |

## Update Rules

- เมื่อสร้าง ticket ให้เพิ่ม Ticket column หรือ link ใน row ที่เกี่ยวข้อง
- เมื่อมี test ให้ใส่ exact test path/name
- Status ใช้ Planned, In Progress, Verified หรือ Deferred
- Deferred ต้องมี decision/ticket อ้างอิง
- Requirement ใหม่ต้องมี unique ID และเพิ่ม matrix
