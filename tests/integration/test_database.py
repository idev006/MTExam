from datetime import date

from sqlalchemy import text

from backend.app.config import Settings
from backend.app.db import Base, Database
from backend.app.db.models import OrgUnit, Person, PersonUnitAssignment


def build_database() -> Database:
    settings = Settings(
        app={"environment": "test"},
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )
    return Database(settings)


def test_sqlite_enforces_foreign_keys() -> None:
    database = build_database()

    try:
        with database.session() as session:
            enabled = session.execute(text("PRAGMA foreign_keys")).scalar_one()
            assert enabled == 1
    finally:
        database.dispose()


def test_portable_models_create_and_persist_foundation_data() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)

    try:
        with database.session() as session:
            division = OrgUnit(code="DIV-01", name="Division 01", level="division")
            person = Person(identifier_hash="hash-001", full_name="สมชาย ทดสอบ")
            session.add_all([division, person])
            session.flush()
            assignment = PersonUnitAssignment(
                person_id=person.id,
                org_unit_id=division.id,
                effective_from=date(2026, 7, 15),
            )
            session.add(assignment)
            session.commit()

        with database.session() as session:
            stored = session.get(Person, person.id)
            assert stored is not None
            assert stored.full_name == "สมชาย ทดสอบ"
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_sqlite_parent_directory_is_created(tmp_path) -> None:
    database_path = tmp_path / "nested" / "mtexam.db"
    settings = Settings(
        app={"environment": "test"},
        database_url=f"sqlite:///{database_path.as_posix()}",
        app_secret_key="test-only-secret",
    )

    database = Database(settings)
    try:
        assert database_path.parent.is_dir()
    finally:
        database.dispose()
