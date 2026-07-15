from __future__ import annotations

from dataclasses import replace

import pytest

from backend.app.config import Settings
from backend.app.domain.employee_import import (
    EmployeeCsvSchemaError,
    EmployeeImportRecord,
    parse_employee_csv,
    reconcile_employee_snapshot,
)
from backend.app.domain.enums import ImportAction

pytestmark = pytest.mark.poc


def employee(cid: str, **changes: object) -> EmployeeImportRecord:
    base = EmployeeImportRecord(
        emp_cid=cid,
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
        emp_status="active",
        emp_descr=None,
    )
    return replace(base, **changes)


def test_csv_uses_toml_header_contract_and_preserves_thai_and_phone() -> None:
    settings = Settings(app={"environment": "test"}, app_secret_key="test-only-secret")
    header_map = settings.personnel_import.columns.model_dump()
    csv_text = (
        "\ufeffemp_cid,emp_fname,emp_lname,emp_status,emp_tel,emp_yod,"
        "emp_position_rank,emp_yod_rank\n"
        "1234567890123,สมชาย,ทดสอบ,active,0812345678,พ.ต.อ.,10,9\n"
    )

    result = parse_employee_csv(
        csv_text.encode("utf-8"),
        header_map=header_map,
        encoding=settings.personnel_import.encoding,
        delimiter=settings.personnel_import.delimiter,
    )

    assert result.is_valid
    assert len(result.records) == 1
    assert result.records[0].emp_fname == "สมชาย"
    assert result.records[0].emp_tel == "0812345678"
    assert result.records[0].emp_position_rank == 10


def test_csv_reports_every_invalid_row_without_exposing_cid_in_message() -> None:
    csv_text = (
        "emp_cid,emp_fname,emp_lname,emp_status,emp_position_rank\n"
        "123,หนึ่ง,ทดสอบ,active,not-a-number\n"
        "123,สอง,ทดสอบ,active,-1\n"
        ",,,active,1\n"
    )

    result = parse_employee_csv(csv_text.encode())

    assert not result.is_valid
    assert not result.records
    assert {error.row_number for error in result.errors} == {2, 3, 4}
    assert {
        "invalid_identifier_format",
        "invalid_integer",
        "duplicate_identifier",
        "negative_rank",
        "required",
    }.issubset({error.code for error in result.errors})
    assert all("123" not in error.message for error in result.errors)


def test_csv_fails_fast_when_required_header_is_missing() -> None:
    with pytest.raises(EmployeeCsvSchemaError, match="emp_status"):
        parse_employee_csv(b"emp_cid,emp_fname,emp_lname\n1234567890123,A,B\n")


def test_full_snapshot_reconciliation_classifies_every_required_action() -> None:
    current = (
        employee("1111111111111"),
        employee("2222222222222"),
        employee("3333333333333"),
        employee("4444444444444"),
        employee("5555555555555", emp_status="inactive"),
    )
    incoming = (
        employee("1111111111111"),
        employee("2222222222222", emp_fname="สมหมาย"),
        employee("3333333333333", emp_kk="สภ.วังทอง"),
        employee("5555555555555", emp_status="active"),
        employee("6666666666666"),
    )

    result = reconcile_employee_snapshot(current, incoming)
    action_by_cid = {item.emp_cid: item.action for item in result}

    assert action_by_cid == {
        "1111111111111": ImportAction.UNCHANGED,
        "2222222222222": ImportAction.CHANGED,
        "3333333333333": ImportAction.MOVED,
        "4444444444444": ImportAction.MISSING,
        "5555555555555": ImportAction.REACTIVATE,
        "6666666666666": ImportAction.ADDED,
    }
    moved = next(item for item in result if item.action is ImportAction.MOVED)
    assert moved.changed_fields == ("emp_kk",)


def test_reconciliation_rejects_duplicate_validated_records() -> None:
    duplicate = employee("1111111111111")

    with pytest.raises(ValueError, match="incoming"):
        reconcile_employee_snapshot((), (duplicate, duplicate))
