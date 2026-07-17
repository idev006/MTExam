# Use-Case Sequence Coverage

**Reviewed:** 2026-07-16

Every use case in the Actor and Use-Case Catalog has a Mermaid sequence diagram. The diagram
file is the behavioral SSOT; this table prevents a new use case from being added without flow
evidence.

| Use case | Sequence heading | Evidence |
|---|---|---|
| UC-AUTH-01 | Login | auth API + session creation |
| UC-AUTH-02 | Logout | confirmation, revoke and redirect |
| UC-ORG-01 | Import personnel CSV snapshot | preview and validation |
| UC-ORG-02 | Review and apply staged personnel import | batch apply and audit |
| UC-SUBJECT-01 | Select/create subject | database subject lookup |
| UC-ADMIN-01 | Manage system settings | authorization and persistence |
| UC-ADMIN-02 | Manage user accounts and roles | account lifecycle and audit |
| UC-QBANK-01 | Author question bank | subject-bound bank lifecycle |
| UC-QBANK-02 | Manage questions inside a bank | question/choice validation |
| UC-PAPER-01 | Publish an Exam Creation | paper publication |
| UC-PAPER-02 | Create Exam Creation and sets | subject, count, scope and variants |
| UC-PAPER-03 | Edit Draft or create Paper revision | Draft invariant, clone lineage and audit |
| UC-EXAM-00 | Create and operate an Exam Window | per-window quota, timing policy, lifecycle and audit |
| UC-EXAM-01 | Start or resume exam | durable session and server deadline |
| UC-EXAM-02 | Answer and autosave/recover | local/API retry path |
| UC-EXAM-03 | Submit exam and reveal result | score finalization |
| UC-REPORT-01 | View scoped report | authorization and read-only query |
| UC-REPORT-02 | View statistics for one Exam Creation | per-creation aggregation |
| UC-AUDIT-01 | Review audit events | filtered immutable audit view |

Source: [Use-Case Sequence Diagrams](use-case-sequence-diagrams.md).
