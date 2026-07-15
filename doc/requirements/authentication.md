# Authentication and Authorization Requirements

**Status:** Baseline approved; SSO is an open decision

## Purpose

ให้เฉพาะผู้มีสิทธิ์เข้าถึงข้อมูลและการทำงานตาม role และ organization scope

## Requirements

### AUTH-001 — Sign in

- ผู้ใช้ active สามารถ sign in ด้วย credential ที่ถูกต้อง
- Credential ผิดต้องตอบข้อความกลางที่ไม่เปิดเผยว่าบัญชีมีอยู่หรือไม่
- บุคคลหรือบัญชี inactive ห้าม sign in
- ทุก sign-in success/failure ที่จำเป็นต้อง audit

### AUTH-002 — Password protection

- Password เก็บเป็น Argon2 hash เท่านั้น
- ห้าม log password หรือ token
- Initial password ต้องถูกเปลี่ยนตาม policy เมื่อเปิดใช้ local account

### AUTH-003 — Session

- Browser release แรกใช้ database-backed opaque session และ `HttpOnly` cookie; ไม่ใช้ JWT เป็น browser session หลัก
- Session มีอายุ absolute 480 นาที และ idle timeout 30 นาที โดยปรับผ่าน typed configuration ได้
- ผู้ใช้ Examinee มี active session ได้ 1 session
- ผู้ใช้กลุ่ม Super/Division/Bureau/Station Admin มี active session ได้ 3 sessions
- Role อื่นมี active session ได้ 1 sessionเป็นค่าเริ่มต้น
- เมื่อ login เกิน limit ระบบ revoke session ที่เก่าที่สุดก่อนสร้าง session ใหม่
- Logout ทำให้ credential ฝั่ง client ใช้งานต่อไม่ได้ทันที
- Session token ต้องเก็บใน database เป็น hash เท่านั้น; ห้ามเก็บ raw token
- Secret มาจาก environment variable
- Production บังคับ HTTPS และ secure cookie หากใช้ cookie

JWT/OIDC จะเพิ่มเป็น authentication adapter ภายหลังเมื่อมี mobile, external API, split frontend
หรือ SSO requirement โดยไม่เปลี่ยน permission/scope contract ของ backend

### AUTH-004 — Role authorization

- API ทุก endpoint ระบุ permission ที่ต้องใช้
- Backend เป็นผู้ตรวจ permission
- การซ่อนปุ่มใน Vue ไม่ถือเป็น security control
- Viewer ไม่มี write permission

### AUTH-005 — Organization scope

- Read scope ของ admin ระดับบนรวมหน่วยลูก
- Write scope จำกัดตาม permission ที่ได้รับ
- Examinee อ่านและแก้ได้เฉพาะ session ของตน
- Scope check ใช้ parent_id hierarchy แบบ database-portable

### AUTH-006 — Account lifecycle

- Import ที่ทำให้ person inactive ต้องปิดการเข้าสู่ระบบ
- การกลับมา active ไม่ควรเปิดบัญชีอัตโนมัติถ้า policy ไม่อนุญาต
- ห้ามลบบัญชีที่มี audit/history

## Roles

Super Admin, Division Admin, Bureau Admin, Station Admin, Exam Author, Examinee และ Viewer ตาม Master Blueprint

## Open Decision

OD-001: local account baseline หรือ SSO ระบบเดิม หากเลือก SSO ต้องเพิ่ม ADR และ threat model ก่อน implement

## Required Tests

- Correct/incorrect sign-in
- Inactive account
- Session limit ต่อ role, oldest-session revocation และ explicit logout
- Absolute/idle expiry และ session token hash storage
- ทุก role ต่อ protected endpoint
- Parent/child scope
- Cross-person session access denied
- Secret ไม่ปรากฏใน response/log
