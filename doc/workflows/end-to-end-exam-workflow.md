# End-to-End Exam Workflow

**Updated:** 2026-07-17
**Status:** Implemented baseline / production human acceptance pending
**Ticket:** EXAM-E2E-005

เอกสารนี้เป็น behavioral overview ตั้งแต่สร้างเนื้อหาจนผู้สอบส่งหรือหมดเวลา โดย backend
เป็นผู้ตัดสิน authorization, organization scope, quota, เวลา คะแนน และการเปิดเผยผลเสมอ

## Swimlane

```mermaid
flowchart LR
    subgraph Author["Exam Author"]
        A1["สร้าง/เผยแพร่ Question Bank"]
        A2["สร้าง Exam Creation: คำถาม ระยะเวลา เกณฑ์ผ่าน quota template"]
        A3["Publish Exam Creation"]
    end
    subgraph Coordinator["Exam Coordinator"]
        C1["เลือก Published Exam Creation ใน scope"]
        C2["กำหนดเวลา quota นโยบายสิ้นสุด และการเปิดเผยผล"]
        C3["เปิด Exam Window"]
        C4["ปิด/ระงับรอบ หรือ force-close session พร้อมเหตุผล"]
    end
    subgraph System["MTExam API / PostgreSQL"]
        S1["ตรวจ role, scope และ lifecycle"]
        S2["snapshot quota และนโยบายของรอบ"]
        S3["resolve หน่วยจริง → quota bucket และ lock quota"]
        S4["สร้าง/คืน session + variant + server deadline"]
        S5["upsert คำตอบและ audit"]
        S6["finalize คะแนนจาก snapshot"]
        S7{"result visibility"}
        S8["audit terminal event"]
    end
    subgraph Examinee["Examinee"]
        E1["เลือกรอบสอบที่เปิด"]
        E2["เริ่ม/กลับเข้าทำต่อ"]
        E3["ตอบและตรวจคำตอบ"]
        E4["ยืนยันส่งผ่าน DaisyUI modal"]
        E5["ดูผลทันที/หลังปิดรอบ หรือรับข้อความไม่เปิดเผย"]
    end

    A1 --> A2 --> S1 --> A3
    A3 --> C1 --> C2 --> S1 --> S2 --> C3
    C3 --> E1 --> E2 --> S3 --> S4 --> E3 --> S5 --> E3
    E3 --> E4 --> S6
    S4 -. "หมดเวลา" .-> S6
    C4 -. "force close" .-> S6
    S6 --> S8 --> S7 --> E5
```

## Sequence — schedule, take, finalize and reveal

```mermaid
sequenceDiagram
    actor A as Exam Author
    actor C as Exam Coordinator
    actor X as Examinee
    participant UI as Vue 3 UI
    participant API as FastAPI
    participant DB as PostgreSQL

    A->>UI: สร้างและ Publish Exam Creation
    UI->>API: POST/PATCH /papers
    API->>DB: ตรวจ owner/scope และบันทึก policy + audit
    C->>UI: จัดรอบสอบจาก Published Paper
    UI->>API: POST /exam-windows พร้อม schedule/quota/result_visibility
    API->>API: ตรวจ coordinator scope และ quota ceiling
    API->>DB: snapshot Window policy + audit
    C->>UI: เปิดรอบสอบ
    UI->>API: PATCH /exam-windows/{id}/status
    API->>DB: เปลี่ยนเป็น open + audit

    X->>UI: เริ่มหรือกลับเข้าทำต่อ
    UI->>API: POST /exam-sessions/windows/{id}/start
    API->>DB: resolve assignment และ SELECT quota FOR UPDATE
    alt มี session เดิม
        DB-->>API: session + saved answers
    else quota และเวลาอนุญาต
        API->>DB: create session, snapshot org/variant/deadline + audit
    else quota เต็ม/นอก scope/นอกเวลา
        API-->>UI: 403/409 โดยไม่สร้าง session
    end
    API-->>UI: questions + answers + server ends_at (ไม่ส่งเฉลย)

    loop ทุกคำตอบก่อน deadline
        X->>UI: เลือกคำตอบ
        UI->>API: PUT /exam-sessions/{id}/answers
        API->>DB: ตรวจ ownership/time/membership และ upsert + audit
        API-->>UI: saved state
    end

    alt ผู้สอบยืนยันส่ง
        X->>UI: กดส่งข้อสอบ
        UI-->>X: DaisyUI modal + จำนวนข้อที่ยังไม่ตอบ
        X->>UI: ยืนยัน
        UI->>API: POST /exam-sessions/{id}/submit
        API->>DB: finalize score และ status=submitted + audit
    else server deadline ผ่าน
        UI->>API: GET/PUT/POST session
        API->>DB: finalize score และ status=timed_out + audit
    else ผู้ควบคุมบังคับปิด
        C->>API: POST /exam-sessions/{id}/force-close + reason
        API->>API: ตรวจ Window ownership/super_admin
        API->>DB: finalize score และ status=force_closed + audit
    end

    API->>API: คำนวณ score/max × 100 และเทียบ passing_percentage
    alt result_visibility=immediate
        API-->>UI: คะแนน เปอร์เซ็นต์ ผ่าน/ไม่ผ่าน และคำอธิบาย
    else after_window_close และรอบยังไม่ปิด
        API-->>UI: terminal status โดยซ่อนผลและคำอธิบาย
    else hidden
        API-->>UI: terminal status โดยไม่เปิดเผยผล
    end
```

## Invariants and operational notes

- การส่งซ้ำคืนผลเดิมและไม่คำนวณ attempt ใหม่
- Unanswered questions ได้ศูนย์ แต่ modal ต้องแจ้งจำนวนก่อนยืนยัน
- `submitted`, `timed_out` และ `force_closed` ใช้ scoring service เดียวกัน
- ผลที่ซ่อนต้องไม่ส่ง score, percentage, pass state หรือ rationale ไปยัง examinee API
- Automatic timeout เป็น request-driven baseline: request ถัดไปที่แตะ session จะ finalize ทันที
  งาน scheduler สำหรับ proactive finalization เป็น operational enhancement ไม่ใช่เงื่อนไขความถูกต้อง
- Window close หยุดการเริ่มใหม่; session แบบ `full_duration` ยังคงใช้ deadline ที่ snapshot ไว้

## Automated evidence

- `tests/api/test_exam_session_lifecycle.py`
- `tests/api/test_system_api.py`
- `tests/integration/test_reporting_postgres.py`
- `frontend/src/components/exam/ExamSubmitPanel.test.ts`

Production Done ยังต้องมี human acceptance บน 360, 768, 1366 และ 1920 px รวมถึง
authenticated workflow load test และ external security sign-off
