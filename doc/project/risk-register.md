# Risk Register

| ID | Risk | Probability | Impact | Mitigation | Owner | Status |
|---|---|---:|---:|---|---|---|
| R-001 | CSV contract ไม่เสถียร | High | High | ขอ sample/owner, version contract, staging validation | PM/PO | Open |
| R-002 | Full snapshot ผิดทำให้ inactive จำนวนมาก | Medium | Critical | Preview, threshold, privileged confirmation, transaction | Backend | Planned |
| R-003 | SQLite ถูกใช้ผิดกับ 500 concurrent | Medium | High | Support profile ชัดเจน, production gate และ load test | Tech Lead | Open |
| R-004 | Database-specific SQL ทำให้สลับ DB ไม่ได้ | Medium | High | Portable rules, CI matrix, architecture tests | Backend | Planned |
| R-005 | Variant shuffle ทำให้เฉลยผิด | Medium | Critical | Stable choice IDs, snapshots, invariant tests | Backend/QA | Planned |
| R-006 | Client timer ถูกใช้เป็น authority | Medium | Critical | Server clock/ends_at, boundary tests | Backend | Planned |
| R-007 | Personnel/score data leakage | Medium | Critical | Scope tests, masking, security review | Security/Backend | Open |
| R-008 | Free host sleep/ephemeral disk | High | High | Hosting validation, persistent DB, cold-start test | Operations | Open |
| R-009 | Requirement/docs drift | Medium | High | DoD, traceability, review gate | PM | Active |
| R-010 | Scope expansion before core works | High | Medium | Kanban WIP, out-of-scope, PM change control | PM/PO | Active |
| R-011 | Unverified 500-user target | High | High | Define workload and load test before promise | Tech Lead | Open |
| R-012 | SSO decision late | Medium | Medium | Local baseline, isolate auth adapter, decision deadline | PO | Open |

## Review Rule

- Project Manager reviews weekly
- Critical risk reviewed before milestone/release
- Closed risk retains history
- New risk receives ticket when mitigation requires work
