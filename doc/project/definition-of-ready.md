# Definition of Ready

Ticket พร้อมเข้าสู่ Ready เมื่อครบทุกข้อที่เกี่ยวข้อง

## Required

- [ ] มี Ticket ID และ owner
- [ ] มี Requirement ID หรือระบุว่าเป็น technical/document task
- [ ] ระบุ outcome และ actor
- [ ] Scope และ out-of-scope ชัดเจน
- [ ] Acceptance criteria ตรวจสอบได้
- [ ] Business rules และ error cases หลักชัดเจน
- [ ] Documents ที่เกี่ยวข้องถูกสร้าง/อัปเดต
- [ ] API/data impact ระบุแล้ว
- [ ] Security/privacy impact ระบุแล้ว
- [ ] Database portability impact ระบุแล้ว
- [ ] Test expectation ระบุแล้ว
- [ ] Dependencies พร้อมหรือมีแผน
- [ ] ไม่มี open decision ที่เปลี่ยน solution อย่างมีนัยสำคัญ
- [ ] งานเล็กพอไหลผ่าน board ได้

## UI Work

- [ ] ระบุหน้าจอ/state/role
- [ ] API contract พร้อมหรือมี mock contract ที่อนุมัติ
- [ ] Local vs Pinia state decision ชัดเจน

## Database Work

- [ ] Model/migration change documented
- [ ] SQLite/MySQL/PostgreSQL behavior considered
- [ ] Rollback/upgrade path considered

## Import Work

- [ ] CSV sample/contract พร้อม
- [ ] Expected added/changed/missing examples
- [ ] Failure and safety gate behavior ชัดเจน

## Exception

Critical production incident เริ่มได้ก่อนเอกสารครบ แต่ต้องมี incident ticket และเติมเอกสาร/tests ก่อน Done
