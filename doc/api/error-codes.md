# API Error Codes

Error code เป็น contract ระหว่าง API, Vue และ tests

## General

| Code | HTTP | Meaning |
|---|---:|---|
| VALIDATION_ERROR | 422 | Field validation failed |
| AUTH_REQUIRED | 401 | Authentication required |
| AUTH_INVALID_CREDENTIALS | 401 | Sign-in failed |
| AUTH_ACCOUNT_INACTIVE | 403 | Account/person inactive |
| FORBIDDEN | 403 | Permission denied |
| RESOURCE_NOT_FOUND | 404 | Not found or not visible |
| STATE_CONFLICT | 409 | Resource state rejects operation |
| SERVICE_UNAVAILABLE | 503 | Required service such as database is unavailable |
| INTERNAL_ERROR | 500 | Unexpected error |

## Personnel Import

| Code | HTTP |
|---|---:|
| IMPORT_FILE_TOO_LARGE | 422 |
| IMPORT_INVALID_ENCODING | 422 |
| IMPORT_INVALID_HEADER | 422 |
| IMPORT_DUPLICATE_FILE | 409 |
| IMPORT_ROW_INVALID | 422 |
| IMPORT_ORG_NOT_FOUND | 422 |
| IMPORT_NOT_READY | 409 |
| IMPORT_ALREADY_APPLIED | 409 |
| IMPORT_MISSING_THRESHOLD | 409 |
| IMPORT_APPLY_FAILED | 409/500 |

## Questions and Papers

| Code | HTTP |
|---|---:|
| QUESTION_CHOICE_COUNT_INVALID | 422 |
| QUESTION_CORRECT_CHOICE_INVALID | 422 |
| QUESTION_ARCHIVED | 409 |
| PAPER_POOL_INSUFFICIENT | 409 |
| PAPER_ALREADY_GENERATED | 409 |
| PAPER_NOT_GENERATED | 409 |
| PAPER_NOT_PUBLISHED | 409 |
| PAPER_VARIANT_GENERATION_FAILED | 409 |

## Exam

| Code | HTTP |
|---|---:|
| EXAM_WINDOW_NOT_OPEN | 409 |
| EXAM_WINDOW_CLOSED | 409 |
| EXAM_NOT_ELIGIBLE | 403 |
| EXAM_SESSION_EXISTS | 409 |
| EXAM_SESSION_NOT_ACTIVE | 409 |
| EXAM_TIMED_OUT | 409 |
| EXAM_ALREADY_SUBMITTED | 409 |
| EXAM_QUESTION_NOT_IN_SESSION | 422 |
| EXAM_CHOICE_NOT_IN_QUESTION | 422 |
| EXAM_ANSWER_LOCKED | 409 |

## Reporting

| Code | HTTP |
|---|---:|
| REPORT_SCOPE_FORBIDDEN | 403 |
| REPORT_FILTER_INVALID | 422 |
| EXPORT_NOT_AVAILABLE | 409 |

## Rules

- Code ใหม่ต้องเพิ่มเอกสารและ tests
- ห้าม reuse code เดิมด้วยความหมายต่างกัน
- Security-sensitive not-found สามารถตอบ RESOURCE_NOT_FOUND แทน forbidden เพื่อไม่เปิดเผย existence
- Frontend แปลข้อความตาม code ได้ แต่ต้องรองรับ fallback message
