# Authentication and Authorization Audit

**Date:** 2026-07-16  
**Scope:** browser authentication, session lifecycle, role authorization and production safeguards

## Implemented controls

- Passwords are stored with Argon2 via `pwdlib`; raw passwords are never persisted.
- Browser sessions use random opaque tokens; only SHA-256 token hashes are stored.
- Cookies are `HttpOnly`, `SameSite=Lax`, and `Secure` in production.
- Absolute session expiry, idle timeout, role-based session limits and server-side revocation are enforced.
- Logout revokes the server session and clears both session and CSRF cookies.
- Inactive accounts/persons invalidate sessions on the next request.
- Failed logins use a dummy hash for unknown usernames to reduce timing/user enumeration and are throttled in a database-backed table across workers (5 failures/15 minutes by default).
- Production state-changing requests with a session cookie require the double-submit CSRF token.
- Role checks deny by default and invalid stored roles fail closed with 403.
- Password change is available to an authenticated user and requires a new 12-character password.
- Super-admin bypass is explicit in the role dependency; it is not an implicit frontend permission.
- Active organization scope is enforced in personnel, content, paper, window, report and audit APIs;
  admin scope replacement is audited as `user.scope.replace`.

## Verification evidence

- Invalid login sequence: five failures return 401, then 429 with `Retry-After`.
- Valid login remains possible for other accounts while one identity is throttled.
- Logout and inactive-account session checks are covered by existing integration tests.
- Backend Ruff and Pytest pass; frontend type-check and production build pass.
- PostgreSQL/MySQL database startup and migration smoke pass; authenticated load smoke completed
  without request failures (50 requests/10 workers, development host).

## Deployment requirements before go-live

- Set a unique `APP_SECRET_KEY` of at least 32 bytes and `APP_ENVIRONMENT=production`.
- Set explicit `CORS_ORIGINS` only to trusted HTTPS origins; do not use wildcard origins with credentials.
- Run `alembic upgrade head` against the production database before starting workers.
- Terminate TLS at the host/proxy and restrict database/network access.
- Configure centralized log monitoring and alert on repeated 429 responses, role-denied events and session revocations.
- Perform dependency scanning, independent penetration testing and production restore-drill acceptance before handling real personal data.

## Known boundary

The current release uses local accounts. SSO is not enabled; the identity provider adapter remains a planned integration and must be reviewed separately before connecting the police identity system.
