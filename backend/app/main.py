from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, select

from backend.app.api.errors import register_exception_handlers
from backend.app.api.middleware import CorrelationIdMiddleware
from backend.app.api.router import api_router
from backend.app.config import PROJECT_ROOT, Settings, get_settings
from backend.app.db.base import Base, utc_now
from backend.app.db.database import Database
from backend.app.db.models import (
    Employee,
    ExamAnswer,
    ExamPaper,
    ExamPaperOrgUnit,
    ExamPaperQuestion,
    ExamSession,
    ExamVariant,
    ExamVariantQuestion,
    ExamWindow,
    ExamWindowScope,
    OrgUnit,
    Person,
    PersonUnitAssignment,
    Question,
    QuestionBank,
    QuestionChoice,
    QuestionVersion,
    Subject,
    UserAccount,
)
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
    _seed_region6_sub_units(db)
    _seed_development_subjects(db)
    accounts = (
        ("demo", "demo1234", "ผู้เข้าสอบสาธิต", UserRole.EXAMINEE),
        ("superadmin", "super1234", "ผู้ดูแลระบบสาธิต", UserRole.SUPER_ADMIN),
        ("author", "author1234", "ผู้สร้างข้อสอบสาธิต", UserRole.EXAM_AUTHOR),
        ("viewer", "viewer1234", "ผู้ตรวจสอบสาธิต", UserRole.VIEWER),
        ("divisionadmin", "division1234", "Division Admin Demo", UserRole.DIVISION_ADMIN),
        ("bureauadmin", "bureau1234", "Bureau Admin Demo", UserRole.BUREAU_ADMIN),
        ("stationadmin", "station1234", "Station Admin Demo", UserRole.STATION_ADMIN),
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
    scope_seed = {
        "demo": "bureau",
        "author": "bureau",
        "divisionadmin": "division",
        "bureauadmin": "bureau",
        "stationadmin": "station",
    }
    for username, level in scope_seed.items():
        seeded_account = db.scalar(
            select(UserAccount).where(UserAccount.username_normalized == username)
        )
        assigned_unit = db.scalar(
            select(OrgUnit).where(OrgUnit.level == level).order_by(OrgUnit.code)
        )
        if level == "division":
            bureau_parent_id = db.scalar(
                select(OrgUnit.parent_id).where(OrgUnit.level == "bureau").order_by(OrgUnit.code)
            )
            if bureau_parent_id is not None:
                assigned_unit = db.get(OrgUnit, bureau_parent_id)
        if (
            seeded_account is not None
            and assigned_unit is not None
            and db.scalar(
                select(PersonUnitAssignment).where(
                    PersonUnitAssignment.person_id == seeded_account.person_id,
                    PersonUnitAssignment.org_unit_id == assigned_unit.id,
                )
            )
            is None
        ):
            db.add(
                PersonUnitAssignment(
                    person_id=seeded_account.person_id,
                    org_unit_id=assigned_unit.id,
                    effective_from=date.today(),
                )
            )
    db.commit()
    _seed_pdpa_question_bank(db)
    _seed_demo_exam_data(db)


def _seed_demo_exam_data(db) -> None:
    """Create an end-to-end exam trail for development and UI demonstrations."""
    columns = {column["name"] for column in inspect(db.bind).get_columns("question_banks")}
    if "subject_id" not in columns:
        return
    bank = db.scalar(select(QuestionBank).where(QuestionBank.name == "PDPA-TH-50"))
    demo = db.scalar(select(UserAccount).where(UserAccount.username_normalized == "demo"))
    author = db.scalar(select(UserAccount).where(UserAccount.username_normalized == "author"))
    bureau = db.scalar(select(OrgUnit).where(OrgUnit.level == "bureau"))
    subject = db.scalar(select(Subject).where(Subject.code == "PDPA"))
    if not all((bank, demo, author, bureau, subject)):
        return

    if db.scalar(select(Employee).where(Employee.emp_cid == "0000000000001")) is None:
        for index in range(1, 11):
            db.add(
                Employee(
                    emp_cid=f"{index:013d}",
                    emp_fname=f"Demo{index}",
                    emp_lname="Examinee",
                    emp_position="ผู้เข้าสอบ",
                    emp_bh="ภ.6",
                    emp_bk=bureau.name,
                    emp_kk="หน่วยทดสอบ",
                    emp_status="active",
                )
            )
    if (
        db.scalar(
            select(PersonUnitAssignment).where(
                PersonUnitAssignment.person_id == demo.person_id,
                PersonUnitAssignment.org_unit_id == bureau.id,
            )
        )
        is None
    ):
        db.add(
            PersonUnitAssignment(
                person_id=demo.person_id,
                org_unit_id=bureau.id,
                effective_from=date.today(),
            )
        )

    paper = db.scalar(select(ExamPaper).where(ExamPaper.title == "PDPA Demo Exam - 10 Questions"))
    if paper is None:
        paper = ExamPaper(
            subject_id=subject.id,
            title="PDPA Demo Exam - 10 Questions",
            question_selection_mode="fixed_set",
            variant_count=1,
            desired_question_count=10,
            default_duration_minutes=60,
            passing_percentage=Decimal("60"),
            status="published",
            org_unit_id=bureau.id,
            created_by=author.person_id,
            published_at=utc_now(),
            revision_number=1,
            updated_at=utc_now(),
            updated_by=author.person_id,
        )
        db.add(paper)
        db.flush()
        paper.family_id = paper.id
        questions = list(
            db.scalars(
                select(Question)
                .where(Question.bank_id == bank.id)
                .order_by(Question.created_at)
                .limit(10)
            )
        )
        db.add_all(
            [
                ExamPaperQuestion(
                    exam_paper_id=paper.id,
                    question_id=question.id,
                    base_order_index=index,
                    score_weight=Decimal("1"),
                )
                for index, question in enumerate(questions)
            ]
        )
        db.add(ExamPaperOrgUnit(exam_paper_id=paper.id, org_unit_id=bureau.id, eligible_count=10))
        db.flush()
    elif paper.passing_percentage is None:
        paper.passing_percentage = Decimal("60")
        quota = db.scalar(
            select(ExamPaperOrgUnit).where(
                ExamPaperOrgUnit.exam_paper_id == paper.id,
                ExamPaperOrgUnit.org_unit_id == bureau.id,
            )
        )
        if quota is not None and quota.eligible_count is None:
            quota.eligible_count = 10

    if paper.family_id is None:
        paper.family_id = paper.id
        paper.updated_at = paper.updated_at or paper.created_at
        paper.updated_by = paper.updated_by or paper.created_by

    window = db.scalar(select(ExamWindow).where(ExamWindow.exam_paper_id == paper.id))
    if window is None:
        now = utc_now()
        window = ExamWindow(
            exam_paper_id=paper.id,
            title="รอบสอบสาธิต PDPA",
            mode="fixed_batch",
            duration_minutes=60,
            completion_policy="fixed_end",
            late_entry_minutes=15,
            window_open_at=now - timedelta(minutes=5),
            window_close_at=now + timedelta(minutes=55),
            status="open",
            created_by=author.person_id,
        )
        db.add(window)
        db.flush()
        db.add(
            ExamWindowScope(
                exam_window_id=window.id,
                org_unit_id=bureau.id,
                eligible_count=10,
            )
        )
    else:
        window_scope = db.scalar(
            select(ExamWindowScope).where(ExamWindowScope.exam_window_id == window.id)
        )
        if window_scope is not None and window_scope.eligible_count is None:
            window_scope.eligible_count = 10

    existing_demo_session = db.scalar(
        select(ExamSession).where(
            ExamSession.exam_window_id == window.id,
            ExamSession.person_id == demo.person_id,
        )
    )
    if existing_demo_session is None:
        variant = db.scalar(select(ExamVariant).where(ExamVariant.exam_paper_id == paper.id))
        if variant is None:
            variant = ExamVariant(
                exam_paper_id=paper.id,
                variant_label="A",
                generation_seed_reference="demo-seed",
            )
            db.add(variant)
            db.flush()
            paper_questions = list(
                db.scalars(
                    select(ExamPaperQuestion)
                    .where(ExamPaperQuestion.exam_paper_id == paper.id)
                    .order_by(ExamPaperQuestion.base_order_index)
                )
            )
            for index, paper_question in enumerate(paper_questions):
                question = db.get(Question, paper_question.question_id)
                choices = list(
                    db.scalars(
                        select(QuestionChoice)
                        .where(QuestionChoice.question_id == question.id)
                        .order_by(QuestionChoice.base_order)
                    )
                )
                version = QuestionVersion(
                    question_id=question.id,
                    content_snapshot=question.content,
                    explanation=question.explanation,
                    choices_snapshot_text=json.dumps(
                        [
                            {
                                "id": str(choice.id),
                                "content": choice.content,
                                "is_correct": choice.is_correct,
                            }
                            for choice in choices
                        ],
                        ensure_ascii=False,
                    ),
                )
                db.add(version)
                db.flush()
                db.add(
                    ExamVariantQuestion(
                        exam_variant_id=variant.id,
                        question_version_id=version.id,
                        order_index=index,
                        choice_display_order_text=json.dumps(
                            [str(choice.id) for choice in choices]
                        ),
                        score_weight=paper_question.score_weight,
                    )
                )
            db.flush()
        now = utc_now()
        session = ExamSession(
            person_id=demo.person_id,
            exam_window_id=window.id,
            exam_variant_id=variant.id,
            examinee_snapshot_text=json.dumps(
                {"username": "demo", "display_name": "Demo Examinee"}
            ),
            org_unit_id=bureau.id,
            eligibility_org_unit_id=bureau.id,
            started_at=now - timedelta(minutes=30),
            ends_at=now + timedelta(minutes=30),
            submitted_at=now - timedelta(minutes=5),
            status="submitted",
            score=Decimal("7"),
        )
        db.add(session)
        db.flush()
        variant_questions = list(
            db.scalars(
                select(ExamVariantQuestion)
                .where(ExamVariantQuestion.exam_variant_id == variant.id)
                .order_by(ExamVariantQuestion.order_index)
            )
        )
        for index, variant_question in enumerate(variant_questions):
            version = db.get(QuestionVersion, variant_question.question_version_id)
            choices = json.loads(version.choices_snapshot_text)
            selected = next(choice for choice in choices if choice["is_correct"])
            if index >= 7:
                selected = choices[1]
            db.add(
                ExamAnswer(
                    exam_session_id=session.id,
                    exam_variant_question_id=variant_question.id,
                    selected_choice_id=UUID(selected["id"]),
                    first_answered_at=now - timedelta(minutes=25),
                    last_updated_at=now - timedelta(minutes=6),
                    is_correct_cache=index < 7,
                )
            )
    elif existing_demo_session.eligibility_org_unit_id is None:
        existing_demo_session.eligibility_org_unit_id = bureau.id
    db.commit()


def _seed_pdpa_question_bank(db) -> None:
    """Load the checked-in 50-question PDPA bank into development SQLite once."""
    # A legacy development database may predate the subject migration. Startup must
    # remain usable so the operator can run Alembic instead of failing during seeding.
    columns = {column["name"] for column in inspect(db.bind).get_columns("question_banks")}
    if "subject_id" not in columns:
        return
    source = PROJECT_ROOT / "data" / "question_banks" / "pdpa_50.json"
    subject = db.scalar(select(Subject).where(Subject.code == "PDPA"))
    owner = db.scalar(select(OrgUnit).where(OrgUnit.code == "POLICE_REGION_6"))
    author = db.scalar(select(UserAccount).where(UserAccount.username_normalized == "author"))
    if not source.exists() or subject is None or owner is None or author is None:
        return
    bank = db.scalar(select(QuestionBank).where(QuestionBank.name == "PDPA-TH-50"))
    if bank is not None:
        return
    payload = json.loads(source.read_text(encoding="utf-8"))
    bank = QuestionBank(
        name="PDPA-TH-50",
        subject_id=subject.id,
        owner_org_unit_id=owner.id,
        is_shared=True,
        status="active",
        created_by=author.person_id,
    )
    db.add(bank)
    db.flush()
    for item in payload["questions"]:
        question = Question(
            bank_id=bank.id,
            content=item["content"],
            explanation=item.get("explanation"),
            difficulty="พื้นฐาน",
        )
        db.add(question)
        db.flush()
        db.add_all(
            [
                QuestionChoice(
                    question_id=question.id,
                    content=choice,
                    is_correct=index == item["correct_index"],
                    base_order=index,
                )
                for index, choice in enumerate(item["choices"])
            ]
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
    db.flush()


def _seed_region6_sub_units(db) -> None:
    """Import the checked-in p6 station file's sub-unit sections idempotently."""
    source = PROJECT_ROOT / "doc" / "p6-station.txt"
    if not source.exists():
        return
    parent_names = {
        "หน่วยงานระดับกองกำกับการใต้หน่วย กองบังคับการอำนวยการตำรวจภูธรภาค 6 (บก.อก.ภ.6)": (
            "BAG_อำนวยการ_ภ6"
        ),
        "กองบังคับการสืบสวนสอบสวนตำรวจภูธรภาค 6 (บก.สส.ภ.6)": "BSS_ภ6",
        "ศูนย์ฝึกอบรมตำรวจภูธรภาค 6 (ศฝร.ภ.6)": "ศฝร_ภ6",
    }
    station_parents = [
        "ภจว_กำแพงเพชร",
        "ภจว_ตาก",
        "ภจว_นครสวรรค์",
        "ภจว_พิจิตร",
        "ภจว_พิษณุโลก",
        "ภจว_เพชรบูรณ์",
        "ภจว_สุโขทัย",
        "ภจว_อุตรดิตถ์",
        "ภจว_อุทัยธานี",
    ]
    station_parent_index = 0
    station_count = 0
    importing_stations = True
    current_parent = None
    child_index = 0
    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if importing_stations:
            if line == "หน่วยงานระดับกองกำกับการใต้หน่วย กองบังคับการอำนวยการตำรวจภูธรภาค 6 (บก.อก.ภ.6)":
                importing_stations = False
                current_parent = db.scalar(
                    select(OrgUnit).where(OrgUnit.code == parent_names[line])
                )
                child_index = 0
                continue
            if not line:
                if station_count:
                    station_parent_index += 1
                    station_count = 0
                continue
            if station_parent_index >= len(station_parents):
                continue
            current_parent = db.scalar(
                select(OrgUnit).where(OrgUnit.code == station_parents[station_parent_index])
            )
            station_count += 1
            if current_parent is not None:
                slug = re.sub(r"[^\w]+", "_", line, flags=re.UNICODE).strip("_")
                code = f"ST_{current_parent.code}_{slug or station_count}"
                if db.scalar(select(OrgUnit).where(OrgUnit.code == code)) is None:
                    db.add(
                        OrgUnit(
                            code=code,
                            name=line,
                            level="station",
                            parent_id=current_parent.id,
                            status=ActiveStatus.ACTIVE,
                        )
                    )
            continue
        if not line or line == "----":
            if line == "----":
                current_parent = None
            continue
        if line in parent_names:
            current_parent = db.scalar(select(OrgUnit).where(OrgUnit.code == parent_names[line]))
            child_index = 0
            continue
        if current_parent is None:
            continue
        child_index += 1
        slug = re.sub(r"[^\w]+", "_", line, flags=re.UNICODE).strip("_")
        code = f"SUB_{current_parent.code}_{slug or child_index}"
        if db.scalar(select(OrgUnit).where(OrgUnit.code == code)) is None:
            db.add(
                OrgUnit(
                    code=code,
                    name=line,
                    level="sub_unit",
                    parent_id=current_parent.id,
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
