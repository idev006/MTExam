from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from backend.app.api.errors import register_exception_handlers
from backend.app.api.middleware import CorrelationIdMiddleware
from backend.app.api.router import api_router
from backend.app.config import PROJECT_ROOT, Settings, get_settings
from backend.app.db.base import Base
from backend.app.db.database import Database
from backend.app.db.models import OrgUnit, Person, Subject, UserAccount
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.domain.security import hash_password


def create_app(settings: Settings | None = None, frontend_dist: Path | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    database = Database(resolved_settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(database.engine)
        if resolved_settings.app.environment in {"development", "test"}:
            with database.session() as db:
                _seed_development_accounts(db)
        yield
        database.dispose()

    app = FastAPI(
        title=resolved_settings.app.name,
        version=resolved_settings.app.version,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.database = database
    app.add_middleware(CorrelationIdMiddleware)
    if resolved_settings.app.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_settings.app.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=resolved_settings.app.api_prefix)
    _mount_frontend_if_built(app, frontend_dist or PROJECT_ROOT / "frontend" / "dist")
    return app


def _seed_development_accounts(db) -> None:
    if db.scalar(select(OrgUnit).where(OrgUnit.code == "DEV")) is None:
        db.add(
            OrgUnit(
                code="DEV",
                name="หน่วยงานสาธิต",
                level="division",
                status=ActiveStatus.ACTIVE,
            )
        )
        db.flush()
    _seed_region6_org_units(db)
    _seed_development_subjects(db)
    accounts = (
        ("demo", "demo1234", "ผู้เข้าสอบสาธิต", UserRole.EXAMINEE),
        ("superadmin", "super1234", "ผู้ดูแลระบบสาธิต", UserRole.SUPER_ADMIN),
        ("author", "author1234", "ผู้สร้างข้อสอบสาธิต", UserRole.EXAM_AUTHOR),
        ("viewer", "viewer1234", "ผู้ตรวจสอบสาธิต", UserRole.VIEWER),
    )
    for username, password, full_name, role in accounts:
        if db.scalar(select(UserAccount).where(UserAccount.username_normalized == username)):
            continue
        person = Person(
            identifier_hash=f"development-{username}",
            full_name=full_name,
            status=ActiveStatus.ACTIVE,
        )
        db.add(person)
        db.flush()
        db.add(
            UserAccount(
                person_id=person.id,
                username_normalized=username,
                password_hash=hash_password(password),
                role=role,
                status=ActiveStatus.ACTIVE,
            )
        )
    db.commit()


def _seed_region6_org_units(db) -> None:
    parent = db.scalar(select(OrgUnit).where(OrgUnit.code == "POLICE_REGION_6"))
    if parent is None:
        parent = OrgUnit(
            code="POLICE_REGION_6",
            name="ตำรวจภูธรภาค 6",
            level="division",
            status=ActiveStatus.ACTIVE,
        )
        db.add(parent)
        db.flush()
    units = (
        ("BAG_อำนวยการ_ภ6", "กองบังคับการอำนวยการตำรวจภูธรภาค 6 (บก.อก.ภ.6)"),
        ("BSS_ภ6", "กองบังคับการสืบสวนสอบสวนตำรวจภูธรภาค 6 (บก.สส.ภ.6)"),
        ("BKC_ภ6", "กองบังคับการกฎหมายและคดีตำรวจภูธรภาค 6 (บก.กค.ภ.6)"),
        ("ศฝร_ภ6", "ศูนย์ฝึกอบรมตำรวจภูธรภาค 6 (ศฝร.ภ.6)"),
        ("ภจว_กำแพงเพชร", "ตำรวจภูธรจังหวัดกำแพงเพชร (ภ.จว.กำแพงเพชร)"),
        ("ภจว_ตาก", "ตำรวจภูธรจังหวัดตาก (ภ.จว.ตาก)"),
        ("ภจว_นครสวรรค์", "ตำรวจภูธรจังหวัดนครสวรรค์ (ภ.จว.นครสวรรค์)"),
        ("ภจว_พิจิตร", "ตำรวจภูธรจังหวัดพิจิตร (ภ.จว.พิจิตร)"),
        ("ภจว_พิษณุโลก", "ตำรวจภูธรจังหวัดพิษณุโลก (ภ.จว.พิษณุโลก)"),
        ("ภจว_เพชรบูรณ์", "ตำรวจภูธรจังหวัดเพชรบูรณ์ (ภ.จว.เพชรบูรณ์)"),
        ("ภจว_สุโขทัย", "ตำรวจภูธรจังหวัดสุโขทัย (ภ.จว.สุโขทัย)"),
        ("ภจว_อุตรดิตถ์", "ตำรวจภูธรจังหวัดอุตรดิตถ์ (ภ.จว.อุตรดิตถ์)"),
        ("ภจว_อุทัยธานี", "ตำรวจภูธรจังหวัดอุทัยธานี (ภ.จว.อุทัยธานี)"),
    )
    for code, name in units:
        if db.scalar(select(OrgUnit).where(OrgUnit.code == code)) is None:
            db.add(
                OrgUnit(
                    code=code,
                    name=name,
                    level="bureau",
                    parent_id=parent.id,
                    status=ActiveStatus.ACTIVE,
                )
            )


def _seed_development_subjects(db) -> None:
    subjects = (
        ("PDPA", "พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล", "แบบทดสอบความรู้พื้นฐาน PDPA"),
        ("GENERAL_POLICE", "ความรู้ทั่วไปสำหรับตำรวจ", "วิชาความรู้ทั่วไป"),
    )
    for code, name, description in subjects:
        if db.scalar(select(Subject).where(Subject.code == code)) is None:
            db.add(Subject(code=code, name=name, description=description, status="active"))


def _mount_frontend_if_built(app: FastAPI, frontend_dist: Path) -> None:
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


app = create_app()
