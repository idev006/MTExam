# Production Security Runbook

## Local Account กับ SSO คืออะไร

ปัจจุบัน MTExam ใช้ Local Account: ระบบเก็บ username และ Argon2 password hash ในฐานข้อมูลของ MTExam เอง ผู้ใช้สมัคร/ถูกสร้างโดย super admin และเข้าสู่ระบบด้วยรหัสของ MTExam

SSO (Single Sign-On) หมายถึง ผู้ใช้เข้าสู่ระบบตำรวจเดิมเพียงครั้งเดียว แล้ว MTExam รับผลยืนยันตัวตนผ่าน OIDC หรือ SAML จาก Identity Provider ของตำรวจ MTExam จะไม่รับหรือเก็บรหัสผ่านตำรวจ แต่จะ map `issuer + subject` ไปยัง `Person/UserAccount`, ตรวจ role และหน่วยงานจาก claims/ข้อมูล master แล้วสร้าง session ภายในเหมือนเดิม

ดังนั้น SSO ไม่ใช่การเปลี่ยนสิทธิ์หรือฐานข้อมูลข้อสอบ แต่เป็นการเปลี่ยนเฉพาะขั้นตอนยืนยันตัวตน ปัจจุบันยังขาดข้อมูล endpoint, client ID, certificate และ claims contract จากระบบตำรวจ จึงยังไม่เปิดใช้ SSO

## Reverse proxy/WAF

ใช้ `deploy/nginx.conf` เป็น baseline หน้า Uvicorn:

- TLS 1.2/1.3 และ HSTS
- จำกัด login ต่อ IP 5 requests/minute
- จำกัด API ทั่วไป 30 requests/second พร้อม burst
- ส่ง `X-Forwarded-*` ให้แอปและให้ Uvicorn เปิด `--proxy-headers` เฉพาะ trusted proxy IP
- WAF ภายนอกควรบล็อก bot, malformed requests และ IP reputation ก่อนถึง Nginx

Application ยังมี database-backed throttle ต่อ username+IP เป็นชั้นที่สอง

## TLS, database network และ secrets

- TLS certificate ต้องออกโดย CA ที่เชื่อถือได้และต่ออายุอัตโนมัติ ห้ามใช้ HTTP ภายนอก
- เปิด database port เฉพาะ private network ให้ API workers; ห้าม expose ต่อ internet
- ใช้ `APP_SECRET_KEY` จาก secret manager/OS secret store ไม่ commit `.env`
- ใช้ database credentials แยกจาก account ผู้ดูแล และให้สิทธิ์เฉพาะ schema ที่จำเป็น
- production ต้องรัน `alembic upgrade head` เป็นขั้นตอน deploy ก่อนเปิด worker

## Penetration-test smoke suite

ก่อน release ต้องยืนยันว่า:

1. ไม่มี password/token ใน response, log หรือ database แบบ raw
2. login ผิดครบ threshold ได้ `429`, account อื่นยัง login ได้
3. session ที่ logout/revoke/inactive ใช้ต่อไม่ได้
4. role ที่ไม่มีสิทธิ์ได้ `403` และไม่เห็นข้อมูลของ endpoint อื่น
5. production state-changing request ที่ไม่มี/มี CSRF token ผิดได้ `403`
6. cookie มี `HttpOnly`, `Secure`, `SameSite=Lax`
7. reverse proxy ไม่ส่งข้อมูลฐานข้อมูลหรือ stack trace ออกภายนอก

การตรวจนี้เป็น security smoke test ไม่แทน penetration test โดยผู้เชี่ยวชาญภายนอก

## Restore drill

สำหรับ SQLite:

```powershell
python scripts/restore_sqlite.py backup data/mtexam.db backups/mtexam-restore-test.db
python scripts/restore_sqlite.py check backups/mtexam-restore-test.db
```

สำหรับ PostgreSQL/MySQL ให้ใช้ `pg_dump/pg_restore` หรือ `mysqldump/mysql` ตาม native tooling และบันทึกเวลา restore, row counts, migration version และผล login/exam/report smoke test
