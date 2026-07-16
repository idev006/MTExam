# Remaining Work Sequence Diagrams

## Authenticated load workflow

```mermaid
sequenceDiagram
    participant L as Load runner
    participant API as MTExam API
    participant DB as PostgreSQL/MySQL
    loop concurrent users
        L->>API: POST /auth/login
        API->>DB: verify account/session
        DB-->>API: account + session
        API-->>L: session cookie + CSRF cookie
        L->>API: GET /reports/summary
        API->>DB: scoped aggregate query
        DB-->>API: metrics
        API-->>L: report response
    end
```

## Restore drill

```mermaid
sequenceDiagram
    participant Ops as Operator
    participant Source as Live database
    participant Backup as Backup artifact
    participant Target as Isolated restore database
    Ops->>Source: dump with ownership/privilege isolation
    Source-->>Backup: binary dump stream
    Ops->>Target: create empty restore database
    Ops->>Target: restore binary dump
    Target-->>Ops: schema/data restored
    Ops->>Target: verify tables, row counts, checksums
    Ops-->>Ops: record RPO/RTO and sign-off
```

## Permission and organization scope update

```mermaid
sequenceDiagram
    participant Admin as super_admin UI
    participant API as User Admin API
    participant DB as Database
    Admin->>API: PUT /admin/users/{id}/scope
    API->>DB: validate active organization IDs
    DB-->>API: validation result
    API->>DB: close current assignments
    API->>DB: insert effective assignments
    API->>DB: write user.scope.replace audit
    API-->>Admin: updated scope
```

## Random-pool paper and preview

```mermaid
sequenceDiagram
    participant Author as Exam author UI
    participant API as Paper API
    participant DB as Database
    Author->>API: POST paper(selection_mode=random_pool, candidates, criteria)
    API->>DB: validate subject/scope/candidate questions
    API->>API: deterministic seed + select desired count
    API->>DB: persist paper and selected questions
    Author->>API: GET /papers/{id}/preview
    API->>DB: load scoped paper/questions
    DB-->>API: questions
    API-->>Author: preview before publish
```

## Personnel import rollback

```mermaid
sequenceDiagram
    participant Admin as super_admin
    participant API as Personnel API
    participant DB as Database
    Admin->>API: POST import/preview
    API->>DB: save batch and validated rows
    Admin->>API: POST import/apply(batch_id)
    API->>DB: save rollback snapshot
    API->>DB: apply employee snapshot
    API->>DB: audit personnel.import
    Admin->>API: POST import/{batch_id}/rollback
    API->>DB: restore snapshot transactionally
    API->>DB: audit personnel.import.rollback
    API-->>Admin: rolled_back
```

## Detailed report export

```mermaid
sequenceDiagram
    participant Viewer as viewer/super_admin
    participant API as Reports API
    participant DB as Database
    Viewer->>API: GET exam-sessions.pdf?status=submitted
    API->>DB: apply role and organization scope
    DB-->>API: session results
    API->>API: render PDF/XLSX
    API-->>Viewer: downloadable report
```

