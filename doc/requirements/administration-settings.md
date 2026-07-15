# Administration and Settings Requirements

## Purpose

Provide a small, role-protected settings area for operational configuration without adding a separate infrastructure service.

## Requirements

- **ADMIN-001** — Only authorized administrators can access system settings.
- **ADMIN-002** — Settings are typed, validated, and persisted through the API; `config/app.toml` remains the non-secret baseline.
- **ADMIN-003** — The UI uses daisyUI controls such as radio, switch, slider, and select where they make choices clearer.
- **ADMIN-004** — The user can choose any enabled daisyUI theme; theme preference is client-side UI state and never changes server authority.
- **ADMIN-005** — Changes show a non-blocking daisyUI feedback message and never use browser alert/confirm dialogs.
- **ADMIN-006** — Every setting change is auditable with actor, timestamp, setting key, and before/after values where safe.
- **ADMIN-007** — Secrets are never rendered back into the UI or written to project documents/logs.

## Initial settings scope

- Session limits and expiry policy
- Exam display page size (number of questions per page)
- Import validation policy and batch limits
- Theme preference and display density
- Read-only system/API/database health

Feature-specific business configuration remains in its owning module. This page is an extension point, not a second business-rule engine.

## Non-functional constraints

- API remains the authority; Vue only presents and submits settings.
- Settings must be covered by pytest API/authorization tests and frontend type-check/build gates.
- No Redis or additional configuration service is required for the initial release.

## Current implementation status

The Vue POC is available at `/settings` with local component state. It deliberately does not claim server persistence until the settings API and authorization endpoint are implemented.
