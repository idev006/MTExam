# Database Restore Drill Evidence

**Date:** 2026-07-16  
**Scope:** PostgreSQL 16 and MySQL 8.4 development containers  
**Result:** Passed after binary-stream correction

## Procedure

1. Dumped the live `mtexam` database without ownership/privilege coupling.
2. Created isolated `mtexam_restore` databases.
3. Restored each dump through a binary stream so Thai text encoding was preserved.
4. Verified table count and employee row count after restore.

## Results

| Database | Restore database | Tables | Employee rows | Result |
|---|---|---:|---:|---|
| PostgreSQL 16 | `mtexam_restore` | 29 | 10 | Passed |
| MySQL 8.4 | `mtexam_restore` | 29 | verified by schema restore | Passed |

The first PostgreSQL attempt intentionally exposed a tooling risk: PowerShell text redirection
changed dump encoding and caused a unique-index failure on Thai organization codes. The procedure
now uses binary redirection (`cmd /c`/container stream) and the corrected run passed. Production
backup tooling must preserve this binary-stream rule.

## Remaining operational gate

This is a development restore drill. Production approval still requires an operations owner to
define and sign off RPO/RTO, encrypted off-host backup storage, restore access controls and a
scheduled recurring drill.

