# Deployment Architecture

## Objective

รองรับ cheap/free hosting โดยใช้ runtime components น้อยที่สุด และไม่ผูกกับ provider

## Mode A — Single Application

แนะนำเป็น default:

    Browser
      → FastAPI
          ├─ /api/v1
          └─ Vue dist static files
      → Database

Build:

1. npm install และ npm run build ใน build environment
2. Copy frontend/dist เข้า application image/directory
3. Install Python dependencies
4. Run Alembic migration
5. Start Uvicorn/FastAPI

Node.js ไม่ต้องอยู่ใน final runtime

## Mode B — Split Static Frontend

    Browser → Static Host
            → FastAPI API → Database

- VITE_API_BASE_URL ระบุ API URL
- API CORS allowlist ระบุ frontend origins
- เหมาะเมื่อมี free static hosting

## Database Choice

- SQLite: ต้องมี persistent disk และ API instance เดียว
- MySQL/PostgreSQL: ใช้ managed/external database ได้
- Ephemeral filesystem ห้ามใช้เก็บ SQLite production data

## Runtime Components

Initial:

- FastAPI process
- Database

Optional only after evidence:

- Reverse proxy for platform requirement/TLS
- Multiple API processes
- External static hosting
- Cache/queue through new ADR

## Configuration

- DATABASE_URL และ secrets จาก hosting environment
- app.toml versioned with application
- VITE_API_BASE_URL ตอน frontend build
- Production environment ห้ามใช้ development defaults

## Release Procedure

1. Confirm release ticket and DoD
2. Backup current database
3. Build pinned frontend/backend dependencies
4. Run tests and migration test
5. Apply migration
6. Deploy application
7. Run health and smoke checks
8. Record version, migration and operator
9. Roll back application if checks fail; database rollback follows tested migration policy

## Health Checks

- Application liveness
- Database connectivity/readiness
- Version endpoint
- ห้าม health response เปิดเผย secret หรือ database credentials

## Backup

- Production backup schedule ขึ้นกับ database/provider
- ต้องมี restore test ไม่ใช่เพียงยืนยันว่ามีไฟล์
- SQLite backup ต้องใช้ safe database backup procedure ไม่ copy ระหว่าง active write แบบสุ่ม
- Retention และ encryption ต้องอนุมัติก่อน production

## Capacity

- Load test ด้วย workload จริงก่อนรับรอง 500 concurrent users
- Record database, instance size, pool size, latency และ error rate
- Free tier sleep/cold start ต้องทดสอบหากนำมาใช้สอบจริง
- ห้ามสัญญา production SLA จาก local test
