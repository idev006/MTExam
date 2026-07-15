# MTExam

ระบบสอบออนไลน์แบบเลือกตอบและจับเวลา พัฒนาแบบ API-first Modular Monolith

## Documentation

เริ่มจาก [Document Index](doc/index.md) และ [Master Blueprint](doc/exam-app-master-blueprint.md)

Project tracking ใช้ [GitHub Project — MTExam Delivery](https://github.com/users/idev006/projects/3/views/1) เป็น status SSOT
และ [Kanban Board Snapshot](doc/project/kanban-board.md) สำหรับรายงานใน repository

## Backend environment

Python ทุกคำสั่งต้องใช้:

    F:\programming\python\MTExam\.venv\Scripts\python.exe

ติดตั้ง dependencies:

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

## Commands

คำสั่งเหล่านี้จะพร้อมหลัง M0 foundation เสร็จ:

    .\.venv\Scripts\python.exe -m pytest
    .\.venv\Scripts\python.exe -m ruff check .
    .\.venv\Scripts\python.exe -m alembic upgrade head
    .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload

Technology POC และ quality gates ทั้ง backend/frontend:

    .\poc\run-poc.ps1

รายละเอียดผลและข้อจำกัดอยู่ที่ [Technology POC](doc/poc/technology-poc.md)

Frontend:

    Set-Location frontend
    npm install
    npm run dev

## Rules

- No Ticket, No Development
- API เป็น System Core
- ไม่มี Personnel CRUD; ข้อมูลมาจาก CSV import
- Source code file ไม่เกิน 800 บรรทัด
- Runtime stack ต้อง minimal
- Core database logic รองรับ SQLite, MySQL และ PostgreSQL
