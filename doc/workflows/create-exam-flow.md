# Create and Publish Exam Workflow

## Actors

Exam Author และ Admin ที่มี permission

## Main Flow

### Current UI flow

1. เลือกรายวิชา — ระบบโหลดคำถามจาก Question Bank ในฐานข้อมูล
2. ค้นหาคำถามและเลือกด้วย checkbox
3. กำหนดจำนวนข้อ; ปุ่มสร้างจะเปิดใช้งานเมื่อเลือกครบตามจำนวน
4. เลือกหน่วยระดับกองบังคับการได้หลายหน่วยงาน
5. กำหนดจำนวน Exam Variants และสร้าง Exam Creation

1. สร้าง/เลือก question bank
2. สร้างคำถามและตัวเลือก
3. Validate ว่ามี 4-5 choices และคำตอบถูกหนึ่งตัว
4. สร้าง exam paper สถานะ draft
5. เลือก fixed_set หรือ random_pool
6. กำหนด score weight และ variant_count
7. Request generation
8. Backend ตรวจ permission และ paper readiness
9. Random pool เลือกคำถามหนึ่งครั้งและบันทึกผล
10. Snapshot question versions
11. Generate variants ด้วย shuffled question/choice order
12. ตรวจ correctness invariant
13. Paper เป็น generated
14. ผู้มีสิทธิ์ publish
15. สร้าง exam window และ organization scopes
16. Window เป็น scheduled/open ตามเวลาและ action

## Fixed Set

- รายการคำถามมาจาก exam_paper_questions
- ห้ามคำถามซ้ำ
- Base order เป็น input ของ generator แต่ variant สลับได้

## Random Pool

- Criteria เป็น portable application data
- Query ดึง candidate อย่าง deterministic ก่อนสุ่ม
- หาก candidate ไม่พอ ตอบ PAPER_POOL_INSUFFICIENT
- ผล selected questions เก็บถาวร

## Generation Failure

- Transaction rollback generation
- Paper ยัง draft
- ไม่มี partial variants
- Audit failure โดยไม่รั่ว answer key

## Immutability

- Generated/published paper ไม่แก้ questions/weights โดยตรง
- ต้องสร้าง revision/new paper ผ่าน ticket/use case ภายหลัง
- Original questions ยังแก้ draft content อื่นได้แต่ snapshot ไม่เปลี่ยน

## Audit Events

paper_created, paper_edited, variant_generated, paper_published, paper_archived, paper_generation_failed

## Tests

อ้าง QBNK-001 ถึง QBNK-005 และ PAPER-001 ถึง PAPER-007
