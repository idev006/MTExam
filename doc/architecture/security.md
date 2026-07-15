# Security Architecture

## Assets

- Credentials และ session/token
- Personal identifiers
- Question content และ answer keys
- Exam answers และ scores
- Audit evidence
- Personnel import files

## Trust Boundaries

- Browser ไม่ trusted
- Uploaded CSV ไม่ trusted
- API เป็น enforcement point
- Database network access จำกัดเฉพาะ application/operations
- Static frontend ไม่มี secret

## Controls

### Authentication

- Password hash ใช้ Argon2 เมื่อใช้ local accounts
- Generic login error
- Account/person inactive เข้าไม่ได้
- Secret จาก environment
- Browser session ใช้ opaque random token ใน `HttpOnly` cookie
- `auth_sessions` เก็บ token hash, expiry, last-seen และ revoke reason; ไม่เก็บ raw token
- Concurrent-session policy: Examinee 1, admin 3, role อื่น 1; เกิน limit revoke oldest
- Logout, idle expiry และ personnel deactivation revoke session ได้
- JWT/OIDC เป็น future adapter สำหรับ mobile/external API/split frontend ไม่ใช่ initial browser authority

### Authorization

- ตรวจ role และ organization scope ทุก protected endpoint
- Object ownership check สำหรับ exam session
- Frontend route guard เป็น UX เท่านั้น
- Default deny เมื่อ permission ไม่ชัดเจน

### Personal data

- Internal foreign key ใช้ person UUID
- Identifier normalize แล้วเก็บ hash สำหรับ lookup
- Reversible value ต้องเข้ารหัสเมื่อจำเป็นตาม integration
- SQLite-first `employee.emp_cid` เก็บ source identifier ตรงตาม contract เพื่อ reconciliation เท่านั้น
- ห้ามใช้ `employee.emp_cid` เป็น public API identifier หรือเขียนลง log; จำกัด file/database access และทบทวน encryption ก่อน production
- Mask identifier ใน UI/log
- กำหนด retention และ access ก่อน production

### Exam integrity

- ไม่ส่ง is_correct ก่อน finalization
- Server-authoritative time
- Submitted/timeout session immutable
- Stable choice ID ป้องกันเฉลยผิดจาก random display
- Audit paper generation และ exam events

### Upload

- จำกัด size, extension และ content format
- Parse เป็น text ไม่ execute content
- Spreadsheet formula ไม่เกี่ยวกับ CSV import; export ต้องป้องกัน formula injection
- เก็บ original file เฉพาะเมื่อ retention/security policy อนุมัติ

### API

- Validate ด้วย Pydantic
- Stable errors ไม่เปิด stack trace
- CORS allowlist เมื่อแยก host
- Production ใช้ HTTPS
- Security headers ที่ hosting layer/application ตามความเหมาะสม

### Database

- Least-privilege account
- Parameterized queries ผ่าน SQLAlchemy
- Backup เข้ารหัสตาม environment capability
- SQLite file permission จำกัด user ที่รัน application

## Audit and Logging

- บันทึก actor, event, subject, UTC time, IP และ correlation ID
- ห้าม log password, token, full identifier และ answer key
- Audit access มี permission แยก
- Application log ไม่ใช่ audit SSOT

## Threat Scenarios to Test

- Examinee อ่าน session คนอื่น
- เปลี่ยน choice ID เป็นข้อที่ไม่อยู่ใน session
- แก้ client clock
- ส่งหลังหมดเวลา
- CSV duplicate/oversized/malformed
- Privilege escalation ผ่าน org ID
- Answer key leakage
- Formula injection ใน CSV export

## Production Gate

ก่อน production ต้อง review:

- SSO/local decision
- HTTPS/cookie policy
- Secret rotation
- Backup restore test
- Data retention
- Audit access
- Vulnerability scan ของ dependencies
