# Production Go/No-Go Decision Record

**วันที่:** 2026-07-16  
**สถานะ:** No-Go pending production evidence  
**ขอบเขต:** MTExam ก่อนนำไปใช้กับข้อมูลบุคลากรและผลสอบจริง

## Decision

ยังไม่ประกาศ Production Go แม้ implementation baseline และ automated tests ผ่านแล้ว
เพราะ production readiness ต้องมีหลักฐานจากระบบ ฐานข้อมูล ความปลอดภัย และการปฏิบัติการจริง
ไม่ใช่เฉพาะผลจาก unit/API tests บน SQLite

## เหตุผลและความเสี่ยง

| รายการ | เหตุผล | ความเสี่ยงหากข้ามขั้นตอน |
|---|---|---|
| MySQL/PostgreSQL integration | SQLite มี transaction, locking, index, UUID และ concurrency ต่างจาก production | migration หรือ query อาจทำงานผิดเมื่อเปลี่ยนฐานข้อมูล |
| Authenticated load test 500 users | health smoke ยังไม่ครอบคลุม login, autosave, resume, submit และ reports พร้อมกัน | ระบบช้า ล่ม หรือข้อมูลชนกันระหว่างการสอบ |
| Independent penetration test | automated tests ไม่ครอบคลุม OWASP, privilege escalation, session abuse, CSRF bypass และ data leakage | ผู้โจมตีอาจเข้าถึงข้อมูลหรือสิทธิ์เกิน role |
| Restore drill | ต้องพิสูจน์ backup ว่ากู้คืนได้จริง ครบถ้วน และอยู่ในเวลาที่ยอมรับได้ | เมื่อระบบเสียอาจกู้ข้อมูลหรือเปิดบริการกลับไม่ได้ |
| Permission matrix และ scope-assignment UI | backend มี scope baseline แต่ต้องยืนยันทุก role/endpoint และให้ admin จัดการขอบเขตได้จริง | ผู้ใช้เห็นหรือแก้ข้อมูลข้ามหน่วยงาน |
| Random-pool paper preview | deterministic snapshot/variant มีแล้ว แต่ยังต้องตรวจ pool criteria และ preview ก่อน publish | ชุดข้อสอบอาจจำนวนหรือเนื้อหาไม่ตรงเงื่อนไข |
| Import rollback | ต้องย้อนกลับ batch CSV ที่ apply ผิดได้โดยไม่ทำลายข้อมูลรอบอื่น | บุคลากรอาจถูกแก้ไขหรือ inactive ผิดจำนวนมาก |
| Detailed result export | summary PDF/XLSX มีแล้ว แต่ต้อง export ผลรายบุคคล รายหน่วย คะแนน คำตอบ และสถานะ | ไม่รองรับงานตรวจสอบและรายงานราชการครบถ้วน |

## Go criteria

เปลี่ยนเป็น **Go** ได้เมื่อมีหลักฐานใน ticket/release record ครบทุกข้อ:

1. migration และ integration tests ผ่านบน SQLite, MySQL และ PostgreSQL
2. authenticated load profile ที่ตกลงกัน (เริ่มต้น 500 users) ผ่าน latency/error/concurrency thresholds
3. penetration test แก้ไขข้อค้นพบระดับ Critical/High และมี sign-off
4. restore drill ผ่าน พร้อมระบุ RPO/RTO และตรวจข้อมูลหลัง restore (development drill now passed; production sign-off remains)
5. permission matrix และ organization scope acceptance ผ่านทุก role ทุก endpoint
6. random-pool preview, import rollback และ detailed result export ผ่าน acceptance tests

จนกว่าจะครบทุกข้อ สถานะ release คือ **No-Go / staging or pilot only**
