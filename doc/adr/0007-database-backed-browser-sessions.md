# ADR-0007: Database-Backed Browser Sessions and Deferred JWT Adapter

**Status:** Accepted
**Date:** 2026-07-15

## Context

MTExam เป็น browser-first single application, ต้อง minimal และต้อง revoke สิทธิ์ได้เมื่อ account/person
ถูกทำให้ inactive จากรอบ CSV import การใช้ stateless JWT เป็น browser session หลักจะทำให้ logout,
session limit และ immediate revocation ซับซ้อนขึ้น

## Decision

- Initial browser authentication ใช้ opaque random session token ใน `HttpOnly` cookie
- เก็บเฉพาะ SHA-256 token hash ใน `auth_sessions`
- จำกัด concurrent active sessions: Examinee 1, admin 3, role อื่น 1
- เมื่อเกิน limit ให้ revoke session ที่เก่าที่สุดแล้วสร้าง session ใหม่
- ค่า limit และ expiry อยู่ใน typed `auth` configuration จาก `config/app.toml`/environment
- JWT/OIDC เป็น future adapter; เปิดใช้เมื่อมี mobile, external API, split frontend หรือ SSO requirement
- ห้ามเพิ่ม Redis เพียงเพื่อ session management

## Consequences

Positive:

- Logout, revoke และ account deactivation มีผลทันที
- ไม่ส่ง credential ไป JavaScript/localStorage
- ใช้ SQLite ได้ใน single-instance deployment และเปลี่ยน database ได้ด้วย SQLAlchemy/Alembic

Trade-offs:

- ทุก authenticated request ต้องอ่าน database หรือใช้ session cache ภายหลังเมื่อมี evidence
- การ scale หลาย instance ต้องใช้ shared database
- JWT future integration ต้องกำหนด key rotation, audience, refresh และ revocation policy แยก
