# MTExam Project Management Plan

**Version:** 1.0
**Status:** Baseline for approval
**Date:** 2026-07-15
**Document owner:** Project Manager
**Review cadence:** ทุก milestone หรือเมื่อ governance เปลี่ยน

## 1. Purpose

เอกสารนี้กำหนดวิธีบริหาร ติดตาม ควบคุม และส่งมอบโครงการ MTExam ให้ทุกคนใช้กระบวนการเดียวกัน ครอบคลุม Product Owner, Project Manager, Technical Lead, Developer, Reviewer, Tester, Operations และ AI coder

เอกสารรายละเอียดที่ใช้งานร่วมกัน:

- [Project Charter](project-charter.md)
- [Roadmap](roadmap.md)
- [Backlog Policy](backlog-policy.md)
- [Definition of Ready](definition-of-ready.md)
- [Definition of Done](definition-of-done.md)
- [Risk Register](risk-register.md)
- [Decision Register](decision-register.md)
- [Dependency Register](dependency-register.md)
- [Authentication and Authorization Audit](security-auth-audit.md)
- [Status Report](status-report.md)
- [Traceability Matrix](../traceability.md)
- Actor/use-case baseline: [Actor and Use-Case Catalog](../use-cases/actor-use-case-catalog.md)
- Interaction evidence: [Use-Case Sequence Diagrams](../workflows/use-case-sequence-diagrams.md)

## 2. Project Management Approach

ใช้แนวทาง:

- Document-Driven Development
- Agile principles
- Kanban flow
- Vertical-slice delivery
- API-first architecture
- Test-driven verification
- Risk-based prioritization

Document-Driven ไม่ใช่ Waterfall เอกสารต้องมีรายละเอียดพอให้พัฒนาและยืนยันผลได้ แล้วอัปเดตเป็น living documents ระหว่างโครงการ

## 3. Management Objectives

- ทุกงานมี owner และติดตามได้
- ทุก feature เชื่อมจาก requirement ไปยัง test และ release
- ลดงานค้างและงานที่เริ่มพร้อมกันมากเกินไป
- ตรวจพบ scope, risk และ dependency เร็ว
- ส่งมอบเป็นส่วนที่ใช้งานได้จริง
- รักษาคุณภาพและความสามารถในการบำรุงรักษา
- ควบคุมการเพิ่มเทคโนโลยีและค่า hosting
- ทำให้คนและ AI coder ใช้ข้อกำหนดเดียวกัน

## 4. Project Management SSOT

| Information | Single Source of Truth |
|---|---|
| Current work status | Project Board |
| Work detail and acceptance | Issue/Ticket |
| Product requirements | doc/requirements |
| Architecture | Blueprint, architecture docs และ ADR |
| Decisions | Decision Register และ ADR |
| Risks | Risk Register |
| Dependencies | Dependency Register |
| Requirement verification | Traceability Matrix |
| Source implementation | Repository |
| API executable schema | FastAPI OpenAPI |
| Release content | Release ticket/note |

ห้ามใช้ spreadsheet หรือ chat เป็นแหล่งสถานะคู่ขนาน หากมีการตัดสินใจใน chat ต้องย้ายเข้าสู่ ticket/register

## 5. Governance

### Product Owner

- กำหนด product priority
- อนุมัติ requirement และ acceptance
- ตัดสิน open product decisions
- รับรอง milestone outcome

### Project Manager

- ดูแล roadmap, backlog และ Project Board
- ตรวจ Definition of Ready และ Definition of Done
- จัดลำดับงานร่วมกับ Product Owner
- ควบคุม WIP, blocker และ dependency
- ดูแล risk, issue, decision และ status reporting
- ประสาน acceptance และ release readiness
- ป้องกัน untracked work และ uncontrolled scope

### Technical Lead

- ดูแล architecture และ technical decisions
- Review database portability, security และ maintainability
- อนุมัติ dependency/infrastructure ใหม่
- ดูแล technical risk และ production readiness

### Developer

- พัฒนาตาม ticket และเอกสาร
- เพิ่ม tests และ migration ที่จำเป็น
- รักษากฎไฟล์ไม่เกิน 800 บรรทัด
- แจ้ง blocker/assumption ทันที
- อัปเดต ticket ก่อนส่ง Review

### Reviewer

- ตรวจ correctness, readability, tests และ security
- ตรวจว่าเอกสารและ implementation ตรงกัน
- ตรวจผลกระทบข้ามฐานข้อมูล
- ห้ามอนุมัติเมื่อ acceptance evidence ไม่ครบ

### Tester / Acceptance Owner

- ตรวจ acceptance criteria
- บันทึก evidence และ defect
- ยืนยัน regression และ boundary cases
- แยก feature gap ออกจาก implementation defect

### Operations

- ดูแล hosting, secret, database, backup และ recovery
- ร่วมทดสอบ deployment และ restore
- บันทึก production change

### AI Coder

- อ่าน ticket และ required documents ก่อนทำงาน
- ไม่ขยาย scope โดยไม่มี ticket/decision
- ใช้ project .venv สำหรับ Python
- เพิ่มหรือแก้ test พร้อม implementation
- รายงานไฟล์ ผลทดสอบ assumption และ risk
- ปฏิบัติตาม Definition of Done เช่นเดียวกับทีม

## 6. RACI Matrix

R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | PO | PM | Tech Lead | Dev | Reviewer/QA | Ops |
|---|---|---|---|---|---|---|
| Product scope | A | R | C | I | C | I |
| Backlog priority | A | R | C | I | I | I |
| Requirement approval | A | R | C | C | C | I |
| Architecture | C | I | A/R | C | C | C |
| Implementation | I | I | C | A/R | C | I |
| Code review | I | I | A/C | C | R | I |
| Acceptance | A | R | C | C | R | I |
| Risk management | C | A/R | C | I | I | C |
| Release readiness | A | R | C | C | C | R |
| Production deployment | I | C | C | I | I | A/R |

ทีมเล็กสามารถให้หนึ่งคนทำหลาย role แต่ accountability ต้องระบุใน ticket/release

## 7. Scope Management

### In-scope baseline

อ้าง [Master Blueprint](../exam-app-master-blueprint.md) และ requirement documents

### Scope rule

    No Ticket → No Development
    No Requirement → Not Ready
    No Test → Not Done
    No Tracker Update → Work Not Complete

### Scope change process

1. สร้าง change ticket
2. ระบุเหตุผลและ expected outcome
3. วิเคราะห์ผลกระทบต่อ requirement, data, API, security, tests, schedule และ hosting
4. Product Owner ตัดสิน product scope
5. Technical Lead ตัดสิน architecture impact
6. Project Manager ปรับ roadmap/backlog
7. อัปเดตเอกสารและ ADR หากจำเป็น
8. จึงเข้าสู่ Ready

ห้ามเพิ่ม capability ระหว่าง In Progress โดยไม่ผ่านกระบวนการ หากจำเป็นให้แยก ticket

## 8. Work Breakdown and Milestones

| Milestone | Main deliverables | Acceptance gate |
|---|---|---|
| M0 Foundation | Repository, CI, backend/frontend shell, config, tests | Health flow และ quality checks ผ่าน |
| M1 Personnel | CSV import, organization, account/scope | Import matrix และ authorization ผ่าน |
| M2 Questions | Banks, questions, papers, variants | Snapshot/invariant tests ผ่าน |
| M3 Examination | Windows, sessions, timer, answers, scoring | End-to-end exam flow ผ่าน |
| M4 Reporting | Reports, CSV export, audit, operations | Acceptance/security/backup checks ผ่าน |
| M5 Hardening | Load, portability, accessibility, release readiness | Production gate ผ่าน |

รายละเอียดอยู่ใน [Roadmap](roadmap.md)

## 9. Kanban Workflow

    Backlog
      → Analysis
      → Ready
      → In Progress
      → Review
      → Verify
      → Done

Blocked เป็น flag ที่ใช้กับทุกสถานะ

### Entry/Exit

| Column | Entry | Exit |
|---|---|---|
| Backlog | Idea/request recorded | Selected for analysis |
| Analysis | Owner assigned | Requirement/impact drafted |
| Ready | DoR passed | Developer pulls work |
| In Progress | Work started | Code/docs/tests ready for review |
| Review | Review evidence attached | Approved or returned |
| Verify | Review passed | Acceptance/DoD passed |
| Done | DoD complete | No further transition |

### WIP Policy

- Developer มีงานหลัก In Progress ได้หนึ่งรายการ
- Team WIP เริ่มต้นไม่เกินจำนวน developers
- Review/Verify ต้องถูก pull ก่อนเริ่มงานใหม่
- PM ปรับ WIP limit ด้วยข้อมูล cycle time/blocking

## 10. Ticket Standard

ทุก ticket ต้องมี:

- Ticket ID
- Requirement ID
- Title เป็น outcome
- Actor/problem/value
- In scope และ out of scope
- Acceptance criteria
- API/data/UI impact
- Security/privacy impact
- Database portability impact
- Dependencies
- Test expectation
- Owner, priority และ milestone
- Links to documents

### Recommended ticket format

    ID:
    Type:
    Requirement:
    Outcome:
    Actor:
    Scope:
    Out of scope:
    Acceptance criteria:
    Technical notes:
    Security/data impact:
    Dependencies:
    Tests:
    Documents:

## 11. Prioritization

ลำดับพิจารณา:

1. Security, data loss และ exam correctness
2. Blocker ของ vertical slice
3. Milestone acceptance requirement
4. Risk reduction และ dependency discovery
5. Maintainability/operational need
6. Optional enhancement

Priority levels:

- Critical
- High
- Medium
- Low

Project Manager และ Product Owner review priority ใน replenishment

## 12. Estimation and Forecasting

- Estimate งานเป็น Small, Medium, Large หรือใช้ story points หากทีมเห็นประโยชน์
- Large item ต้องพิจารณาแบ่ง vertical slice
- Forecast ใช้ throughput และ cycle time หลังมีข้อมูลจริง
- ห้ามใช้ estimate เป็น commitment โดยไม่มี dependency/capacity review
- Research ที่ไม่แน่นอนใช้ time-boxed spike และต้องได้ decision/evidence

## 13. Schedule and Cadence

| Activity | Cadence | Owner | Output |
|---|---|---|---|
| Replenishment | Weekly | PM/PO | Ready queue |
| Daily sync | Workday, short | Team | Blockers/flow |
| Risk/dependency review | Weekly | PM | Updated registers |
| Demo/review | Every 1-2 weeks | PM/Team | Acceptance feedback |
| Retrospective | Every 2-4 weeks | PM/Team | Improvement actions |
| Architecture review | As needed/milestone | Tech Lead | ADR/decision |
| Status report | Weekly or milestone | PM | Stakeholder summary |
| Release readiness | Per release | PM/Ops | Go/no-go record |

## 14. Communication Plan

| Audience | Information | Channel/artifact |
|---|---|---|
| Delivery team | Work status/blockers | Project Board + daily sync |
| Product Owner | Scope, decisions, demo | Tickets + review |
| Technical team | Architecture/quality | ADR + review |
| Operations | Deployment/dependency | Release ticket/runbook |
| Sponsor | Milestone, risk, forecast | Status report |

การตัดสินใจที่กระทบโครงการต้องบันทึก ไม่ถือข้อความสนทนาเป็น approval ถาวร

## 15. Quality Management

Quality gates:

- Approved acceptance criteria
- pytest unit/API/integration
- Database portability matrix
- Ruff
- Alembic migration checks
- Security deny-path tests
- No source file over 800 lines
- Document and traceability review
- Acceptance verification

Critical quality invariants:

- Stable choice ID และ correct answer ทุก variant
- Server-authoritative timer
- No personnel/history hard delete
- No cross-scope data access
- Import apply transaction/rollback

รายละเอียดอยู่ใน [Testing Strategy](../architecture/testing-strategy.md)

## 16. Risk Management

Process:

1. Identify risk
2. Assess probability and impact
3. Assign owner
4. Define mitigation/trigger
5. Create work ticket when action is required
6. Review weekly
7. Close with evidence; retain history

Critical risk ต้อง escalate ทันทีและอาจหยุด release

Risk SSOT: [Risk Register](risk-register.md)

## 17. Issue and Blocker Management

Issue คือปัญหาที่เกิดขึ้นแล้ว Risk คือสิ่งที่อาจเกิด

Blocker record ต้องมี:

- Description
- Blocked ticket/milestone
- Impact
- Owner
- Next action
- Needed decision/dependency
- Next review date

Escalation:

- Critical security/data/correctness: immediate to PM, Tech Lead และ PO
- Blocked มากกว่าหนึ่ง working day: PM review
- External dependency เกิน agreed date: stakeholder escalation

## 18. Dependency Management

- Internal dependency link ระหว่าง tickets
- External dependency อยู่ Dependency Register
- งานไม่เข้า Ready ถ้า dependency สำคัญยังไม่พร้อม เว้นแต่มี mock/assumption ที่อนุมัติ
- Dependency ใหม่มี owner และ needed-by date
- Package/infrastructure ใหม่ผ่าน technical approval

## 19. Decision Management

- Product decision บันทึกใน Decision Register
- Architecture decision ที่มีผลระยะยาวสร้าง ADR
- Open decision มี owner, default และ needed-by milestone
- Decision เปลี่ยนต้องบันทึกเหตุผลและ impact ไม่ลบประวัติ

## 20. Change and Configuration Management

- Source code และ documents version controlled
- requirements.txt pin Python dependencies
- package-lock.json lock Frontend dependencies
- config/app.toml เป็น non-secret configuration SSOT
- Environment variables เก็บ secrets
- Database migrations versioned ด้วย Alembic
- Release ต้องระบุ application version และ migration version

## 21. Release Management

### Current implementation gate

The repository currently delivers an MVP/POC with verified vertical slices. The authoritative
production decision is maintained in [Release Readiness Checklist](release-readiness-checklist.md).
`Verify` is not production approval. Before a ticket moves to `Done`, update its requirement row,
test evidence, use-case documentation when behavior changes, Kanban status and status report.

### Use-case completion governance

The [Use-Case Implementation Status](use-case-implementation-status.md) document is the
implementation status SSOT for use-case completeness. An API skeleton alone is not complete:
authorization, UI path, persistence, failure path, automated test, sequence evidence and
operational acceptance are required. P0 items are release blockers and must be visible on GitHub Project.

### Release readiness

- Scope/acceptance ผ่าน
- DoD ผ่านทุก ticket
- Tests/database matrix ผ่านตาม release profile
- Migration และ rollback/backup plan พร้อม
- Risk ไม่มี unresolved Critical
- Deployment/health/smoke procedure พร้อม
- Stakeholder go/no-go บันทึก

### Release flow

1. Freeze release candidate scope
2. Run quality gates
3. Backup/verify restore readiness
4. Build from pinned dependencies
5. Apply migration
6. Deploy
7. Health/smoke checks
8. Record outcome
9. Rollback/escalate เมื่อ fail

## 22. Status Reporting

### Current production backlog (2026-07-16)

The authoritative remaining-use-case list is [Production Use-Case Backlog](production-use-case-backlog.md).
P0 items are release blockers; P1 items are required before broad rollout. The Project Manager must
create or link one GitHub Project ticket per backlog row and attach acceptance evidence before moving
the row to Done.

Weekly/milestone status อย่างน้อยมี:

- Overall RAG status
- Completed
- In Progress
- Next
- Milestone forecast
- Blockers/issues
- Top risks
- Open decisions
- Dependency changes
- Quality/release status

Project Board เป็น live status ส่วน [Status Report](status-report.md) เป็น periodic snapshot

## 23. Metrics

Flow:

- Cycle time
- Work item age
- Throughput
- WIP
- Blocked time

Quality:

- Escaped defects
- Test pass rate
- Requirement verification coverage
- Migration/database matrix result
- Oversized source files

Delivery:

- Milestone acceptance
- Critical risk age
- Open decision age

Metrics ใช้ปรับระบบการทำงาน ไม่ใช้จัดอันดับ/กดดันรายบุคคล

## 24. Procurement and Cost Control

- Initial architecture ใช้ service ขั้นต่ำ
- Free/cheap hosting ต้องผ่าน persistent storage, sleep/cold-start และ capacity checks
- Infrastructure ใหม่ต้องระบุ cost, operational owner และ measured need
- PM track recurring cost และ renewal risk ก่อน production

## 25. Project Closure

โครงการ/phase ปิดเมื่อ:

- Accepted deliverables ครบ
- Open defects/risks transferred หรือ accepted
- Documents, runbooks และ credentials ownership ส่งมอบ
- Backup/restore และ operations handover ผ่าน
- Project Board/tickets final
- Lessons learned บันทึก
- Final status และ approval ลงนาม

## 26. Current Baseline

ณ 2026-07-15:

- Documentation baseline จัดทำแล้ว
- Git repository, GitHub Issues และ GitHub Project `MTExam Delivery` initialized
- M0 Backend, Frontend, configuration, schema, migration และ quality gates implemented
- Technical verification ผ่านบน SQLite, local frontend build และ GitHub CI run 29407299728
- GitHub Project เป็น status SSOT และ migrate งานเริ่มต้นเป็น 10 Issues แล้ว
- Human acceptance ของ M0 ยัง pending
- MySQL/PostgreSQL connected verification ยัง pending
- Approved sample personnel CSV ยังเป็น M1 blocker

## 27. Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Product Owner | TBD | Pending | |
| Project Manager | TBD | Pending | |
| Technical Lead | TBD | Pending | |
| Operations/Security | TBD | Pending | |

เมื่อยังไม่ลงนาม เอกสารนี้ใช้เป็น working baseline และ open decisions/defaults ตาม Decision Register
