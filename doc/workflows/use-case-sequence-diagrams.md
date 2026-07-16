# Use-Case Sequence Diagrams

Diagrams below describe the API-first flow. Vue is a client of the API; it is never the authority for identity, authorization, score, or durable exam state.

## UC-AUTH-01 — Login

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Vue Login
    participant API as Auth API
    participant DB as SQLite
    U->>UI: Submit username/password
    UI->>API: POST /auth/login
    API->>DB: Find active account and verify hash
    DB-->>API: Account + role
    API->>DB: Create AuthSession
    API-->>UI: User profile + HttpOnly cookie
    UI-->>U: Redirect to role-allowed page
```

## UC-AUTH-02 — Logout

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Vue App
    participant M as ConfirmModal
    participant API as Auth API
    participant DB as SQLite
    U->>UI: Click Logout
    UI->>M: Open confirmation
    U->>M: Confirm
    M-->>UI: confirm event
    UI->>API: POST /auth/logout
    API->>DB: Revoke AuthSession
    API-->>UI: 200 + delete cookie
    UI->>UI: Clear current user
    UI-->>U: Redirect /login
```

## UC-ORG-01 — Import personnel CSV snapshot

```mermaid
sequenceDiagram
    actor A as super_admin
    participant UI as Import UI
    participant API as Import API
    participant S as Staging/Domain
    participant DB as SQLite
    A->>UI: Select CSV and import
    UI->>API: Upload CSV + idempotency key
    API->>S: Parse, validate, reconcile snapshot
    S-->>API: Add/change/missing/warning result
    API->>DB: Transactionally apply current-state rows
    API-->>UI: Summary + row errors
    UI-->>A: Show non-blocking result and audit reference
```

## UC-ORG-02 — Review and apply staged personnel import

```mermaid
sequenceDiagram
    actor A as super_admin
    participant UI as Import UI
    participant API as Personnel API
    participant DB as SQLite
    A->>UI: Upload CSV
    UI->>API: POST /personnel/import/preview
    API->>DB: Create import batch and row staging
    API-->>UI: Batch id, valid/invalid rows and reconciliation summary
    A->>UI: Confirm apply
    UI->>API: POST /personnel/import/apply {batch_id}
    API->>DB: Apply valid snapshot in transaction
    API->>DB: Mark batch applied and write audit event
    API-->>UI: Added/changed/missing summary
```

## UC-ADMIN-01 — Manage system settings

```mermaid
sequenceDiagram
    actor A as super_admin
    participant UI as Settings UI
    participant API as Settings API
    participant DB as SQLite
    A->>UI: Change typed control
    UI->>API: PUT /settings
    API->>API: Authenticate and authorize role
    API->>DB: Validate and persist before/after
    API-->>UI: Saved settings
    UI-->>A: DaisyUI toast, no browser alert
```

## UC-ADMIN-02 — Manage user accounts and roles

```mermaid
sequenceDiagram
    actor A as super_admin
    participant UI as User Administration UI
    participant API as User Admin API
    participant DB as SQLite
    A->>UI: Create, deactivate or change role
    UI->>API: POST/PUT /admin/users
    API->>API: Authenticate and authorize super_admin
    API->>DB: Validate account and persist lifecycle change
    API->>DB: Write audit before/after metadata
    API-->>UI: Updated account and status
    UI-->>A: Show DaisyUI success/error feedback
```

## UC-AUDIT-01 — Review audit events

```mermaid
sequenceDiagram
    actor A as super_admin
    participant UI as Audit UI
    participant API as Audit API
    participant DB as SQLite
    A->>UI: Open audit log and set filters
    UI->>API: GET /audit?event_type=...&subject_type=...
    API->>API: Authenticate and authorize super_admin
    API->>DB: Query immutable audit events
    DB-->>API: Filtered events with actor and metadata
    API-->>UI: Paginated audit rows
    UI-->>A: Render read-only timeline/table
```

## UC-QBANK-01 — Author question bank

```mermaid
sequenceDiagram
    actor E as exam_author
    participant UI as Authoring UI
    participant API as Question API
    participant DB as SQLite
    E->>UI: Create/edit draft question
    UI->>API: POST/PUT question draft
    API->>API: Check author scope and validate choices
    API->>DB: Save new immutable version
    API-->>UI: Draft/version status
    E->>UI: Request publish
    UI->>API: POST /question-banks/{id}/publish
    API->>DB: Mark version active + audit
    API-->>UI: Published bank
```

## UC-QBANK-02 — Manage questions inside a bank

```mermaid
sequenceDiagram
    actor E as exam_author
    participant UI as Question Bank UI
    participant API as Question API
    participant DB as SQLite
    E->>UI: Select subject and draft bank
    UI->>API: GET /question-banks/{bank_id}/questions
    API->>DB: Load questions and choices
    DB-->>API: Question list
    API-->>UI: Render question cards
    E->>UI: Enter question, choices and one correct answer
    UI->>API: POST /question-banks/{bank_id}/questions
    API->>API: Validate 2-10 choices and exactly one correct
    API->>DB: Save question, choices and audit event
    API-->>UI: Draft question id
    E->>UI: Publish bank
    UI->>API: POST /question-banks/{bank_id}/publish
    API->>DB: Verify questions and choices; set bank active
    API-->>UI: Published bank
```

## UC-PAPER-01 — Publish an Exam Creation

```mermaid
sequenceDiagram
    actor E as exam_author
    participant UI as Paper UI
    participant API as Paper API
    participant DB as SQLite
    E->>UI: Select active questions and rules
    UI->>API: POST /papers
    API->>DB: Save paper, questions, variant seed
    API-->>UI: Draft paper
    E->>UI: Publish paper
    UI->>API: POST /papers/{id}/publish
    API->>DB: Validate invariants and publish
    API-->>UI: Published paper ready for exam window
```

## UC-SUBJECT-01 — Select/create subject

```mermaid
sequenceDiagram
    actor E as exam_author
    participant UI as Authoring UI
    participant API as Question API
    participant DB as SQLite
    E->>UI: Open subject selector
    UI->>API: GET /question-banks/subjects
    API->>DB: Read active subjects
    DB-->>API: Subject list
    API-->>UI: Subject options
    E->>UI: Create subject when authorized
    UI->>API: POST /question-banks/subjects
    API->>DB: Save unique subject code + audit
    API-->>UI: Subject
```

## UC-PAPER-02 — Create Exam Creation and sets

```mermaid
sequenceDiagram
    actor E as exam_author
    participant UI as Paper UI
    participant API as Paper API
    participant DB as SQLite
    E->>UI: Select subject, question count, allowed bureaus and variants
    UI->>API: POST /papers with subject_id, desired_question_count and allowed_org_unit_ids
    API->>DB: Save independent ExamPaper creation
    API->>DB: Generate/attach ExamVariant sets
    API-->>UI: Draft Exam Creation and set count
    E->>UI: Publish creation
    UI->>API: POST /papers/{id}/publish
    API->>DB: Validate and publish
    API-->>UI: Published creation ready for exam window
```

## UC-REPORT-02 — View statistics for one Exam Creation

```mermaid
sequenceDiagram
    actor V as viewer/exam_author
    participant UI as Report UI
    participant API as Reporting API
    participant DB as SQLite
    V->>UI: Choose subject or Exam Creation
    UI->>API: GET /reports/exam-creations?subject_id=...
    API->>DB: Query ExamPaper to ExamVariant to ExamSession
    DB-->>API: Counts and scores scoped to one creation
    API-->>UI: Per-creation statistics
    UI-->>V: Show variants, participants, submitted and average score
```

## UC-EXAM-01 — Start or resume exam

```mermaid
sequenceDiagram
    actor X as examinee
    participant UI as Exam UI
    participant API as Exam API
    participant DB as SQLite
    X->>UI: Open exam
    UI->>API: GET current user and resume session
    API->>DB: Find in-progress session for user/window
    alt Existing session
        DB-->>API: Session + saved answers
    else New session
        API->>DB: Create session with server timestamps
    end
    API-->>UI: Questions, status, expires_at, answered map
    UI-->>X: Show progress and navigator
```

The production session endpoints are `POST /exam-sessions/windows/{window_id}/start` and
`GET /exam-sessions/{session_id}`. The API creates the immutable question-version snapshot and
returns the server `ends_at` deadline.

## UC-EXAM-02 — Answer and autosave/recover

```mermaid
sequenceDiagram
    actor X as examinee
    participant UI as Exam UI
    participant Local as Browser recovery store
    participant API as Exam API
    participant DB as SQLite
    X->>UI: Select answer
    UI->>Local: Persist answer immediately
    UI->>API: PUT answer (retry-safe)
    alt Online
        API->>DB: Upsert answer and update activity
        DB-->>API: Saved timestamp
        API-->>UI: synced
    else Offline/API unavailable
        API-->>UI: network error
        UI-->>X: Show offline/pending state
        UI->>Local: Keep pending mutation
    end
    X->>UI: Refresh or reopen later
    UI->>API: Load session
    UI->>API: Retry pending mutations
```

## UC-EXAM-03 — Submit exam and reveal result

```mermaid
sequenceDiagram
    actor X as examinee
    participant UI as Exam UI
    participant API as Exam API
    participant DB as SQLite
    X->>UI: Click submit
    UI-->>X: Show unanswered summary and confirm modal
    X->>UI: Confirm
    UI->>API: Sync pending answers
    UI->>API: POST /exam-sessions/{id}/submit
    API->>DB: Transaction: validate, calculate score, mark submitted
    DB-->>API: Immutable result
    API-->>UI: Score/result
    UI-->>X: Show score, answers, and rationales
```

Submission is idempotent: repeating the submit request returns the stored result rather than
recalculating a different score.

## UC-REPORT-01 — View scoped report

```mermaid
sequenceDiagram
    actor V as viewer
    participant UI as Report UI
    participant API as Reporting API
    participant DB as SQLite
    V->>UI: Open report
    UI->>API: GET /reports
    API->>API: Authenticate, authorize, apply scope
    API->>DB: Query read-only aggregates
    DB-->>API: Scoped rows/summary
    API-->>UI: Report data without secrets
    UI-->>V: Render table/chart/export action
```

## UC-REPORT-03 — Filter, drill down and export

```mermaid
sequenceDiagram
    actor U as Reporting user
    participant UI as Vue Reports UI
    participant API as Reporting API
    participant Scope as Role/Organization Scope
    participant DB as PostgreSQL
    U->>UI: Select subject, creation, window, date and organization
    UI->>API: GET /reports/dashboard with shared filters
    API->>Scope: Resolve visible papers and descendant organizations
    Scope-->>API: Allowed paper/org IDs
    API->>DB: Aggregate quota, sessions, scores and people in scope
    DB-->>API: KPI, charts, breakdown and page
    API-->>UI: Dashboard + generated_at
    U->>UI: Open person detail
    UI->>API: GET /reports/people/{session_id}
    API->>Scope: Re-check session scope
    API->>DB: Read immutable result and write audit event
    API-->>UI: Answers, correctness and rationale
    U->>UI: Export PDF/XLSX/CSV
    UI->>API: GET /reports/export with identical filters
    API->>DB: Repeat scoped aggregation and write export audit
    API-->>U: Filtered file
```

## UC-REPORT-04 — Reserve organization quota at exam start

```mermaid
sequenceDiagram
    actor X as Examinee
    participant API as Exam Session API
    participant Scope as Assignment/Quota Resolver
    participant DB as PostgreSQL
    X->>API: POST /exam-sessions/windows/{id}/start
    API->>Scope: Resolve active actual unit to configured quota unit
    Scope->>DB: SELECT quota FOR UPDATE
    Scope->>DB: Count sessions for window and quota unit
    alt Capacity available
        API->>DB: Create session with actual and quota organization snapshots
        API-->>X: Session started
    else Quota full
        API-->>X: 409 Organization exam quota is full
    end
```
