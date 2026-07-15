# Definition of Done

## Requirement and Documentation

- [ ] Acceptance criteria ผ่าน
- [ ] Requirement/architecture/workflow ตรงกับ implementation
- [ ] Decision ใหม่บันทึกใน register/ADR
- [ ] Traceability matrix อัปเดต

## Code

- [ ] Business logic อยู่ layer ที่ถูกต้อง
- [ ] ไม่มี source file เกิน 800 lines
- [ ] ไม่มี secret/credential ใน repository
- [ ] ไม่มี dependency ที่ไม่ได้อนุมัติ
- [ ] Code อ่านง่ายและไม่มี dead code ที่รู้แล้ว

## Tests

- [ ] Unit tests ผ่าน
- [ ] API/integration tests ที่เกี่ยวข้องผ่าน
- [ ] Regression test สำหรับ bug
- [ ] Database support matrix ที่เกี่ยวข้องผ่าน
- [ ] Ruff ผ่าน
- [ ] Test รันด้วย project .venv

## Data and API

- [ ] Migration upgrade ผ่าน
- [ ] Data model document อัปเดต
- [ ] API schema/error code อัปเดต
- [ ] Authorization deny paths ทดสอบ
- [ ] ไม่มี sensitive data leakage

## Frontend

- [ ] ใช้ Vue Composition API convention
- [ ] Pinia ใช้เฉพาะ global state
- [ ] Loading/error/empty states ครบ
- [ ] Keyboard/basic accessibility ตรวจแล้ว

## Delivery

- [ ] Review ผ่าน
- [ ] Verification/acceptance ผ่าน
- [ ] Ticket และ Project Board อัปเดต
- [ ] Known risks บันทึก
- [ ] Release note เมื่อเป็น user-visible change

งานที่ยังติดข้อใดข้อหนึ่งไม่เป็น Done แม้ code เขียนเสร็จ
