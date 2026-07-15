import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from backend.app.config import Settings
from backend.app.db import Base, Database
from backend.app.db.models import Employee


def build_database() -> Database:
    settings = Settings(
        app={"environment": "test"},
        database_url="sqlite:///:memory:",
        app_secret_key="test-only-secret",
    )
    return Database(settings)


def test_employee_schema_matches_approved_contract() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)

    try:
        inspector = inspect(database.engine)
        columns = {column["name"]: column for column in inspector.get_columns("employee")}
        primary_key = inspector.get_pk_constraint("employee")

        assert list(columns) == [
            "emp_cid",
            "emp_yod",
            "emp_fname",
            "emp_lname",
            "emp_position",
            "emp_position_rank",
            "emp_yod_rank",
            "emp_gender",
            "emp_tel",
            "emp_bh",
            "emp_bk",
            "emp_kk",
            "emp_status",
            "emp_descr",
            "created_dt",
            "updated_dt",
        ]
        assert primary_key["constrained_columns"] == ["emp_cid"]
        assert columns["emp_cid"]["type"].length == 13
        assert columns["emp_fname"]["nullable"] is False
        assert columns["emp_lname"]["nullable"] is False
        assert columns["emp_status"]["nullable"] is False
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_employee_persists_thai_data_and_system_timestamps() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)

    try:
        employee = Employee(
            emp_cid="1234567890123",
            emp_yod="พ.ต.อ.",
            emp_fname="สมชาย",
            emp_lname="ทดสอบ",
            emp_position="ผู้กำกับการ",
            emp_position_rank=10,
            emp_yod_rank=9,
            emp_gender="ชาย",
            emp_tel="0812345678",
            emp_bh="ภ.6",
            emp_bk="ภ.จว.พิษณุโลก",
            emp_kk="สภ.เมืองพิษณุโลก",
            emp_descr="ข้อมูลทดสอบ",
        )
        with database.session() as session:
            session.add(employee)
            session.commit()

        with database.session() as session:
            stored = session.get(Employee, employee.emp_cid)
            assert stored is not None
            assert stored.emp_fname == "สมชาย"
            assert stored.emp_tel == "0812345678"
            assert stored.emp_status == "active"
            assert stored.created_dt is not None
            assert stored.updated_dt >= stored.created_dt
            original_updated_dt = stored.updated_dt
            stored.emp_fname = "สมชายแก้ไข"
            session.commit()
            assert stored.updated_dt > original_updated_dt
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_employee_rejects_duplicate_cid() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)

    try:
        with database.session() as session:
            session.add(Employee(emp_cid="1234567890123", emp_fname="หนึ่ง", emp_lname="ทดสอบ"))
            session.commit()

        with pytest.raises(IntegrityError):
            with database.session() as session:
                session.add(
                    Employee(emp_cid="1234567890123", emp_fname="สอง", emp_lname="ทดสอบ")
                )
                session.commit()
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()


def test_employee_rejects_negative_rank_scores() -> None:
    database = build_database()
    Base.metadata.create_all(database.engine)

    try:
        with pytest.raises(IntegrityError):
            with database.session() as session:
                session.add(
                    Employee(
                        emp_cid="1234567890123",
                        emp_fname="สมชาย",
                        emp_lname="ทดสอบ",
                        emp_position_rank=-1,
                    )
                )
                session.commit()
    finally:
        Base.metadata.drop_all(database.engine)
        database.dispose()
