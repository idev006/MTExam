# Decision Register

| ID | Date | Decision | Status | Reference |
|---|---|---|---|---|
| D-001 | 2026-07-15 | รองรับ individual และ fixed batch | Approved | Blueprint |
| D-002 | 2026-07-15 | API เป็น System Core | Approved | ADR-0002 |
| D-003 | 2026-07-15 | Modular Monolith multi-tier | Approved | ADR-0001 |
| D-004 | 2026-07-15 | Vue 3 Composition API บน Vite | Approved | Frontend architecture |
| D-005 | 2026-07-15 | Vue Router และ Pinia เฉพาะ global state | Approved | Frontend architecture |
| D-006 | 2026-07-15 | Tailwind CSS + daisyUI | Approved | Frontend architecture |
| D-007 | 2026-07-15 | Minimal runtime ไม่มี Redis initial | Approved | ADR-0003 |
| D-008 | 2026-07-15 | Personnel/org มาจาก CSV ไม่มี manual CRUD | Approved | ADR-0004 |
| D-009 | 2026-07-15 | รองรับ SQLite/MySQL/PostgreSQL | Approved | ADR-0005 |
| D-010 | 2026-07-15 | SQLAlchemy synchronous baseline | Approved | Backend architecture |
| D-011 | 2026-07-15 | config/app.toml เป็น non-secret config SSOT | Approved | Configuration |
| D-012 | 2026-07-15 | Document-Driven + Agile/Kanban | Approved | ADR-0006 |
| D-013 | 2026-07-15 | Source code file ไม่เกิน 800 lines | Approved | Testing strategy |
| D-014 | 2026-07-15 | Python ใช้ project .venv เท่านั้น | Approved | Backend architecture |
| D-015 | 2026-07-15 | Project Board เป็น status SSOT | Approved | Project charter |
| D-016 | 2026-07-15 | Anti-cheat initial ใช้ shuffle เท่านั้น | Approved | Blueprint |
| D-017 | 2026-07-15 | ประกาศผลทันทีหลัง finalization | Approved | Scoring requirement |
| D-018 | 2026-07-15 | ใช้ SQLite เป็นฐานข้อมูลเริ่มต้น | Approved | Database portability |
| D-019 | 2026-07-15 | Employee table/header ใช้ชื่อ `emp_*` ตาม contract | Approved | Personnel import requirement |
| D-020 | 2026-07-15 | Browser ใช้ DB-backed session; Examinee 1/admin 3; JWT เป็น future adapter | Approved | ADR-0007 |
| D-021 | 2026-07-15 | Vue container/page template, daisyUI feedback, and daisyUI theme store | Approved | ADR-0008 |

## Open Decisions

| ID | Question | Default | Needed by | Owner |
|---|---|---|---|---|
| OD-001 | Local auth หรือ SSO | Local baseline | Before production auth integration | PO |
| OD-002 | Shared question bank | false | M2 | PO |
| OD-003 | Late entry policy | Allow with warning | M3 | PO |
| OD-004 | Export PDF/Excel | CSV only | M4 | PO |
| OD-006 | Audit/data retention | No destructive cleanup | Before production | Sponsor/Security |

## Decisions added 2026-07-16

- D-022: Question banks can be shared across organizations; exam-window bureau scope remains the enforcement boundary.
- D-023: Release 1 uses local accounts; SSO will be a replaceable identity-provider adapter later.
- D-024: Admin configures late-entry grace minutes for scheduled batch windows.
- D-025: PDF is the first report export format; Excel is the next compatible exporter.
- D-026: Exam content authoring and new Exam Window scheduling are separated. `exam_coordinator`
  owns new operations within assigned organization scope; authors retain creator-only lifecycle
  access solely for historical Windows so active rounds are not orphaned.

## Rule

Approved decision เปลี่ยนได้ด้วย ticket, impact analysis และ update เอกสาร/ADR ไม่แก้ย้อนหลังโดยลบเหตุผลเดิม
