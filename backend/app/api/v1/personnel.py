from __future__ import annotations

# ruff: noqa: E501
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import Employee, UserAccount
from backend.app.domain.employee_import import parse_employee_csv
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.services.audit import record_audit

router = APIRouter(prefix="/personnel", tags=["personnel"])


class EmployeeResponse(BaseModel):
    emp_cid: str
    emp_fname: str
    emp_lname: str
    emp_yod: str | None
    emp_position: str | None
    emp_bh: str | None
    emp_bk: str | None
    emp_kk: str | None
    emp_status: str


class ImportRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class ImportResponse(BaseModel):
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    added_count: int
    changed_count: int
    missing_count: int


class ImportPreviewResponse(ImportResponse):
    errors: list[dict[str, object]] = []


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.VIEWER)),
    ],
) -> list[EmployeeResponse]:
    rows = db.scalars(select(Employee).order_by(Employee.emp_cid))
    return [EmployeeResponse.model_validate(row, from_attributes=True) for row in rows]


@router.post("/import", response_model=ImportResponse)
def import_snapshot(
    payload: ImportRequest,
    db: Annotated[Session, Depends(get_db_session)],
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> ImportResponse:
    try:
        parsed = parse_employee_csv(payload.content.encode("utf-8-sig"))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if parsed.errors:
        return ImportResponse(
            filename=payload.filename,
            status="validation_failed",
            total_rows=len(parsed.records) + len(parsed.errors),
            valid_rows=len(parsed.records),
            invalid_rows=len(parsed.errors),
            added_count=0,
            changed_count=0,
            missing_count=0,
        )
    incoming = {record.emp_cid: record for record in parsed.records}
    current = {row.emp_cid: row for row in db.scalars(select(Employee))}
    added = changed = 0
    for cid, record in incoming.items():
        row = current.get(cid)
        if row is None:
            row = Employee(emp_cid=cid)
            db.add(row)
            added += 1
        elif any(
            getattr(row, field) != getattr(record, field)
            for field in record.__dataclass_fields__
            if field != "emp_cid"
        ):
            changed += 1
        for field in record.__dataclass_fields__:
            setattr(row, field, getattr(record, field))
    missing = 0
    for cid, row in current.items():
        if cid not in incoming and row.emp_status != ActiveStatus.INACTIVE:
            row.emp_status = ActiveStatus.INACTIVE
            missing += 1
    db.commit()
    record_audit(db, actor_person_id=_account.person_id, event_type="personnel.import", subject_type="employee_snapshot", metadata={"filename": payload.filename, "added": added, "changed": changed, "missing": missing})
    db.commit()
    return ImportResponse(
        filename=payload.filename,
        status="applied",
        total_rows=len(parsed.records),
        valid_rows=len(parsed.records),
        invalid_rows=0,
        added_count=added,
        changed_count=changed,
        missing_count=missing,
    )


@router.post("/import/preview", response_model=ImportPreviewResponse)
def preview_snapshot(
    payload: ImportRequest,
    _account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> ImportPreviewResponse:
    try:
        parsed = parse_employee_csv(payload.content.encode("utf-8-sig"))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ImportPreviewResponse(
        filename=payload.filename,
        status="valid" if parsed.is_valid else "validation_failed",
        total_rows=len(parsed.records) + len(parsed.errors),
        valid_rows=len(parsed.records),
        invalid_rows=len(parsed.errors),
        added_count=0,
        changed_count=0,
        missing_count=0,
        errors=[
            {
                "row_number": error.row_number,
                "field": error.field,
                "code": error.code,
                "message": error.message,
            }
            for error in parsed.errors
        ],
    )


@router.post("/import/apply", response_model=ImportResponse)
def apply_snapshot(
    payload: ImportRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> ImportResponse:
    return import_snapshot(payload, db, account)
