# Database and Performance Verification

## Portable database verification

The SQLAlchemy model layer is compiled against SQLite, MySQL, and PostgreSQL dialects in the existing POC suite. Before release, the CI environment must run Alembic upgrade and API integration tests against live MySQL and PostgreSQL services. SQLite remains the local/default database.

## Load smoke check

With Uvicorn running:

```powershell
.\.venv\Scripts\python.exe poc/load_smoke.py --requests 100 --workers 10
```

This is a repeatable smoke check, not a production capacity claim. A release load test must include authenticated login, autosave, report queries, and concurrent submissions, with a target of 500 users recorded in the release evidence.
