# ADR-0008: Vue Container Component and DaisyUI UX Standard

- Status: Accepted
- Date: 2026-07-15
- Decision owner: Engineering

## Context

The frontend must remain easy to change while the API remains the system core. Pages also need consistent layout, feedback, theme selection, and test seams without adding another UI framework.

## Decision

Use a three-level Vue component convention:

1. **Application/layout** components own global shell concerns such as navigation and theme initialization.
2. **Page/container** components own route-level orchestration: API calls, composables, local state, Pinia access when cross-page state is required, and navigation decisions. They compose layout and presentational components.
3. **Presentational** components render props and emit user intent. They do not call APIs or make business decisions.

`PageContainer` and `PageHeader` are the baseline page template. New pages should use them unless a documented exception exists.

Use daisyUI components/tokens first. User feedback must use reusable daisyUI feedback components (`AppAlert`, `AppToast`, `ConfirmModal`); browser `alert`, `confirm`, and `prompt` are prohibited. Theme selection uses daisyUI themes through `data-theme`, with the selected theme persisted locally and managed by a small Pinia store.

## Consequences

- Layout and styling changes are centralized and do not require rewriting page orchestration.
- Containers can be tested with mocked API/composable boundaries; presentational components can be tested with props/events.
- Pinia remains selective: theme is global UI state, while page filters/forms remain local.
- Enabling all daisyUI themes increases CSS size, but keeps deployment simple and supports the product requirement for user-selectable themes.

## Verification

- `npm run type-check`
- `npm run build`
- pytest architecture checks prohibit browser modal APIs and enforce source-size limits.
