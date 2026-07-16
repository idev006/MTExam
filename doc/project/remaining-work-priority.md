# Remaining Work Priority Register

**Updated:** 2026-07-16  
**Release status:** Production Candidate / Staging-Pilot; Production Go is not approved

รายการนี้เป็นลำดับงานคงค้างที่ต้องใช้ติดตามร่วมกับ Kanban และ Release Readiness Checklist
โดยเรียงตามความเสี่ยงต่อความถูกต้อง ความปลอดภัย และการเปิดใช้งานจริง

| ลำดับ | งาน | สถานะ | เหตุผลที่ต้องทำ |
|---:|---|---|---|
| 1 | Authenticated load test ระดับ 500 users | profile ผ่าน 0 failures / performance ค้าง | 500-request summary profile ผ่าน แต่ p95 11.20s; ยังไม่ครอบคลุม exam workflow และยังไม่มี production latency threshold |
| 2 | Independent penetration test และ security sign-off | security smoke เสร็จ / external ค้าง | automated smoke ตรวจ boundary/throttle แล้ว แต่ไม่แทนการตรวจ OWASP, privilege escalation, session, CSRF และ data leakage |
| 3 | Production restore sign-off | ค้าง | dev restore ผ่านแล้ว แต่ต้องกำหนด RPO/RTO, encrypted off-host backup และ recurring drill |
| 4 | Permission matrix ครบทุก role/endpoint | admin reporting roles added / full matrix ค้าง | `division_admin`, `bureau_admin`, `station_admin` now access scoped reports; ต้องยืนยันทุก endpoint และกรณีข้ามหน่วยงาน |
| 5 | Admin UI สำหรับ role และ organization scope | implementation เสร็จ / device acceptance ค้าง | admin แก้ role, active/inactive และหน่วยงานได้โดยไม่ใช้ database direct access |
| 6 | Random-pool acceptance | implementation เสร็จ / acceptance ค้าง | ต้องยืนยัน subject, difficulty, tag, จำนวนข้อ และ preview ผ่าน UI/API |
| 7 | Audit coverage 100% | baseline เพิ่ม / full coverage ค้าง | ต้องตรวจทุก mutation ให้มี actor, before/after, IP, correlation ID และ retention policy |
| 8 | Detailed report PDF | implementation เสร็จ / acceptance ค้าง | ต้องรับรองผลรายบุคคล/รายหน่วย คะแนน คำตอบ และสถานะสำหรับงานตรวจสอบ |
| 9 | UI acceptance ทุก device | build เสร็จ / acceptance ค้าง | ต้องทดสอบ smartphone, tablet, notebook และ PC ด้วย workflow จริง |
| 10 | Police SSO integration | รอ dependency | ต้องมี OIDC/SAML metadata, claims mapping, certificate และ logout endpoint จากเจ้าของระบบ |

Administrative reporting note: development accounts `divisionadmin/division1234`,
`bureauadmin/bureau1234` and `stationadmin/station1234` are seeded for acceptance; each sees
its assigned organization and active descendants only.

## Completion rule

รายการจะย้ายเป็น `Done` เมื่อมี implementation, authorization, failure-path, automated test,
เอกสาร/sequence evidence และ operational acceptance ครบตาม Definition of Done

Sequence evidence: [Remaining Work Sequences](diagrams/remaining-work-sequences.md)

Reporting UI/UX and implementation baseline: [Reporting UI/UX Design](reporting-ui-ux-design.md).
The reporting backlog must follow its REPORT-UX/API/UI/EXP/QA tickets and must not be marked
Done until pass/fail, attendance, drill-down, export and responsive acceptance are evidenced.

Implementation update 2026-07-16: pass/fail and attendance tied to Exam Creation, quota enforcement,
role-scoped dashboard, ECharts, person drill-down and filter-consistent PDF/XLSX/CSV are implemented
with backend/frontend automated tests. Local four-breakpoint browser acceptance passed; production
device sign-off, load threshold and external security acceptance remain open, therefore REPORT-QA-08
remains `Verify`, not `Done`.

Automated gate scripts are under `poc/` and can be orchestrated with
`scripts/run-production-gates.ps1`. External sign-offs remain intentionally manual.

## Release rule

Production Go ต้องรอรายการ 1–5 และ 7–10 มีหลักฐานครบ ส่วนรายการ 6 ต้องผ่าน acceptance ก่อนเปิดใช้
random-pool ในการสอบจริง
