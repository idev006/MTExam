# Production Operations Runbook

## Pre-deployment

1. Set `APP_ENV=production`; do not use development seed accounts.
2. Provide a secret session signing/configuration value and a production database URL via
   environment variables or the hosting secret store; never commit secrets to `config/app.toml`.
3. Run Alembic migrations and the complete test/build gates from the release checklist.
4. Confirm HTTPS, secure cookie settings, CORS allow-list and an application health check.

## SQLite backup and restore

Create a timestamped, hashed backup with:

```powershell
.\scripts\backup_sqlite.ps1 -Database data/mtexam.db -OutputDirectory backups
```

Restore only during a maintenance window: stop the API, copy the verified backup to the
database path, run migrations, start the API and execute the health/API smoke checks. Keep at
least three recent backups and perform a restore drill before every production release.

## Monitoring and incident response

- Monitor `/health` and HTTP 5xx/correlation IDs.
- Preserve audit logs and database backups as incident evidence.
- If an exam timer or submit path is unavailable, stop opening new windows, keep existing
  sessions recoverable, and record the incident before resuming.
