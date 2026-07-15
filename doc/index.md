# MTExam Document Index

**Document owner:** Project Manager  
**Last reviewed:** 2026-07-15  

หน้านี้เป็นจุดเริ่มต้นสำหรับคน ทีมพัฒนา ผู้ทดสอบ และ AI coder ทุกคน ต้องอ่าน Master Blueprint และเอกสารที่เกี่ยวข้องกับ ticket ก่อนเริ่มงาน

## Core

- [Master Blueprint](exam-app-master-blueprint.md)
- [Traceability Matrix](traceability.md)

## Requirements

- [Personnel and Organization Import](requirements/personnel-import.md)
- [Authentication and Authorization](requirements/authentication.md)
- [Question Bank](requirements/question-bank.md)
- [Exam Paper and Variant](requirements/exam-paper.md)
- [Exam Session](requirements/exam-session.md)
- [Scoring](requirements/scoring.md)
- [Reporting and Audit](requirements/reporting.md)

## Architecture

- [System Architecture](architecture/system-architecture.md)
- [Backend Architecture](architecture/backend-architecture.md)
- [Frontend Architecture](architecture/frontend-architecture.md)
- [Data Model](architecture/data-model.md)
- [Database Portability](architecture/database-portability.md)
- [Configuration](architecture/configuration.md)
- [Security](architecture/security.md)
- [Testing Strategy](architecture/testing-strategy.md)
- [Deployment](architecture/deployment.md)

## Workflows

- [Personnel Import Flow](workflows/personnel-import-flow.md)
- [Create and Publish Exam Flow](workflows/create-exam-flow.md)
- [Take Exam Flow](workflows/take-exam-flow.md)

## API

- [API Conventions](api/conventions.md)
- [Error Codes](api/error-codes.md)

Executable OpenAPI is generated from FastAPI after the application exists ห้ามแก้ generated OpenAPI ด้วยมือ

## Project Management

- [Project Management Plan](project/project-management-plan.md)
- [Kanban Board](project/kanban-board.md)
- [Project Charter](project/project-charter.md)
- [Roadmap](project/roadmap.md)
- [Backlog Policy](project/backlog-policy.md)
- [Definition of Ready](project/definition-of-ready.md)
- [Definition of Done](project/definition-of-done.md)
- [Risk Register](project/risk-register.md)
- [Decision Register](project/decision-register.md)
- [Dependency Register](project/dependency-register.md)
- [Status Report](project/status-report.md)

## Architecture Decision Records

- [ADR-0001 Modular Monolith](adr/0001-modular-monolith.md)
- [ADR-0002 API as System Core](adr/0002-api-as-system-core.md)
- [ADR-0003 Minimal Infrastructure](adr/0003-minimal-infrastructure.md)
- [ADR-0004 Personnel CSV Import](adr/0004-personnel-csv-import.md)
- [ADR-0005 Database Portability](adr/0005-database-portability.md)
- [ADR-0006 Document-Driven Delivery](adr/0006-document-driven-delivery.md)

## Required Reading by Work Type

| Work type | Required documents |
|---|---|
| Any code change | Blueprint, ticket requirement, DoR, DoD, testing strategy |
| Backend/API | System architecture, backend architecture, API conventions |
| Frontend | Frontend architecture, API conventions |
| Database | Data model, database portability, migration rules |
| Personnel import | Personnel requirement and import workflow |
| Exam engine | Exam paper, exam session, scoring and take-exam workflow |
| Release | Deployment, risk register, status report and DoD |

## Document Change Rule

- เอกสารที่เปลี่ยนพฤติกรรมต้องเชื่อมกับ ticket
- Decision สำคัญต้องมี ADR หรือ decision register entry
- ผู้แก้เอกสารต้องอัปเดตวันที่ review เมื่อเนื้อหาได้รับการตรวจแล้ว
- งานยังไม่ Done หากเอกสารไม่ตรงกับ implementation
