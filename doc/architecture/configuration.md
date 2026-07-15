# Configuration

## Sources

- config/app.toml: non-secret application configuration
- Environment variables: secrets และ deployment-specific connection
- frontend .env: public VITE-prefixed build configuration

## Precedence

1. Environment secrets/allowed deployment overrides
2. app.toml
3. Typed defaults ที่จำเป็นจริง

ห้ามมีค่า default เดียวกันซ้ำหลายไฟล์

## Example app.toml

    [app]
    name = "MTExam"
    environment = "development"
    api_prefix = "/api/v1"
    timezone = "Asia/Bangkok"

    [database]
    pool_size = 10
    max_overflow = 10
    pool_timeout_seconds = 30

    [exam]
    default_duration_minutes = 60
    minimum_questions = 1
    maximum_questions = 200
    allow_answer_revision = true
    show_result_after_submit = true

    [exam.batch]
    allow_late_entry = true
    minimum_remaining_minutes = 5

    [personnel_import]
    mode = "full_snapshot"
    encoding = "utf-8-sig"
    delimiter = ","
    maximum_file_size_mb = 20
    reject_duplicate_file = true
    missing_person_warning_percent = 10

    [personnel_import.columns]
    person_identifier = "person_id"
    full_name = "full_name"
    rank = "rank"
    org_unit_code = "org_unit_code"
    org_unit_name = "org_unit_name"
    org_unit_level = "org_unit_level"
    parent_org_unit_code = "parent_org_unit_code"
    status = "status"

    [audit]
    enabled = true
    record_ip_address = true
    record_user_agent = true

## Environment Variables

Required candidates:

    DATABASE_URL
    APP_SECRET_KEY
    INITIAL_ADMIN_PASSWORD

Rules:

- ห้าม commit actual secret
- ห้ามส่ง secret ไป public-config
- Startup ต้อง fail fast เมื่อ required setting ขาดหรือ type ผิด
- Log แสดงชื่อ setting ที่ผิดได้ แต่ห้ามแสดงค่า secret

## Frontend

    VITE_API_BASE_URL=/api/v1

VITE variables เป็น public build-time values ห้ามเก็บ secret

## Public Configuration API

Frontend รับเฉพาะค่าที่ต้องแสดง/ใช้ UX เช่น maximum upload size หรือ policy แสดงผล ห้ามอ่าน app.toml โดยตรง

## Change Control

- การเปลี่ยน policy ที่กระทบ user ต้องมี ticket และ requirement update
- การเพิ่ม setting ต้องมี typed model, default/required rule และ test
- Setting ที่ไม่ถูกใช้ต้องลบ ไม่สะสม feature flags ที่ไม่มี owner
