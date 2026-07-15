# Backlog and Kanban Policy

## Board

    Backlog → Analysis → Ready → In Progress → Review → Verify → Done

Blocked เป็น flag พร้อมเหตุผลและ owner ไม่ใช่ที่พักงานแบบไม่มีกำหนด

## Work Item Types

- Feature
- Bug
- Technical
- Security
- Documentation
- Research/Spike

## Required Fields

- Ticket ID
- Title/outcome
- Requirement ID
- Type and priority
- Owner
- Acceptance criteria
- Dependencies
- Documents
- Target milestone/release
- Test expectation

## Priority

| Priority | Meaning |
|---|---|
| Critical | Security/data loss/exam correctness/release blocker |
| High | Required milestone capability |
| Medium | Valuable but not blocking current outcome |
| Low | Improvement/backlog option |

## WIP

- แต่ละ developer มี In Progress หลักหนึ่งรายการ
- Team WIP limit ปรับตาม team size แต่ Review/Verify ต้องไม่ค้าง
- ห้ามเริ่มงานใหม่เพื่อหลีกเลี่ยงการแก้ blocker ของงานเดิม

## Ready Policy

เฉพาะงานผ่าน Definition of Ready เข้า Ready

## Pull Policy

Developer ดึงงาน priority สูงสุดที่ skill/dependency พร้อม ไม่เลือกงานสะดวกโดยข้าม priority โดยไม่มีการตกลง

## Blocked Policy

ภายในวันทำงานเดียวต้องระบุ:

- Blocking condition
- Impact
- Owner ผู้แก้
- Next check date
- Alternative work ถ้ามี

Project Manager review blocker ทุก cadence

## Change Policy

- Scope เพิ่มระหว่าง In Progress ต้องกลับ Analysis หรือแยก ticket
- Bug ที่พบใน acceptance ของ ticket เดิมแก้ใน ticket หากอยู่ใน scope
- New capability แยก ticket

## Done Policy

เฉพาะงานผ่าน Definition of Done ย้าย Done ห้ามใช้ Done แทน deployed/accepted หากยังไม่ผ่าน

## Cadence

- Replenishment weekly
- Short daily sync
- Review/demo every 1-2 weeks
- Retrospective every 2-4 weeks
- Release on completed vertical slice and readiness

## Metrics

- Cycle time
- Work item age
- Throughput
- Blocked time
- Escaped defects

ไม่ใช้ velocity เพื่อกดดันรายบุคคล
