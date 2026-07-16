from __future__ import annotations

# ruff: noqa: E501
import json
from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.v1.auth import require_roles
from backend.app.db.dependencies import get_db_session
from backend.app.db.models import (
    Employee,
    OrgUnit,
    PersonnelImportBatch,
    PersonnelImportRow,
    UserAccount,
)
from backend.app.domain.employee_import import EmployeeImportRecord, parse_employee_csv
from backend.app.domain.enums import ActiveStatus, UserRole
from backend.app.services.audit import record_audit
from backend.app.services.org_authorization import active_org_unit_ids

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
    batch_id: str | None = None
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


class ImportApplyRequest(BaseModel):
    batch_id: UUID | None = None
    filename: str | None = None
    content: str | None = None


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[
        UserAccount,
        Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.EXAM_AUTHOR, UserRole.VIEWER)),
    ],
) -> list[EmployeeResponse]:
    rows = list(db.scalars(select(Employee).order_by(Employee.emp_cid)))
    if account.role != UserRole.SUPER_ADMIN:
        allowed_ids = active_org_unit_ids(db, account)
        allowed_units = list(db.scalars(select(OrgUnit).where(OrgUnit.id.in_(allowed_ids))))
        allowed_names = {value for unit in allowed_units for value in (unit.name, unit.code)}
        rows = [row for row in rows if row.emp_bk in allowed_names or row.emp_kk in allowed_names]
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
    return _apply_records(db, parsed.records, payload.filename, _account.person_id, parsed.errors)


def _apply_records(db: Session, records: list, filename: str, actor_person_id, errors: list) -> ImportResponse:
    incoming = {record.emp_cid: record for record in records}
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
    record_audit(db, actor_person_id=actor_person_id, event_type="personnel.import", subject_type="employee_snapshot", metadata={"filename": filename, "added": added, "changed": changed, "missing": missing})
    db.commit()
    return ImportResponse(
        filename=filename,
        batch_id=None,
        status="applied",
        total_rows=len(records),
        valid_rows=len(records),
        invalid_rows=0,
        added_count=added,
        changed_count=changed,
        missing_count=missing,
    )


@router.post("/import/preview", response_model=ImportPreviewResponse)
def preview_snapshot(
    payload: ImportRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> ImportPreviewResponse:
    try:
        parsed = parse_employee_csv(payload.content.encode("utf-8-sig"))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    batch = PersonnelImportBatch(filename=payload.filename, file_checksum=__import__("hashlib").sha256(payload.content.encode()).hexdigest(), uploaded_by=account.person_id, status="ready" if parsed.is_valid else "validation_failed", total_rows=len(parsed.records) + len(parsed.errors), valid_rows=len(parsed.records), invalid_rows=len(parsed.errors))
    db.add(batch)
    db.flush()
    for index, record in enumerate(parsed.records, start=2):
        db.add(PersonnelImportRow(batch_id=batch.id, row_number=index, raw_data_text=json.dumps(asdict(record), ensure_ascii=False), normalized_identifier_hash=__import__("hashlib").sha256(record.emp_cid.encode()).hexdigest(), validation_status="valid", action="pending"))
    db.commit()
    record_audit(db, actor_person_id=account.person_id, event_type="personnel.import.preview", subject_type="personnel_import_batch", subject_id=batch.id, metadata={"filename": payload.filename, "valid_rows": len(parsed.records), "invalid_rows": len(parsed.errors)})
    db.commit()
    return ImportPreviewResponse(
        batch_id=str(batch.id),
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
    payload: ImportApplyRequest,
    db: Annotated[Session, Depends(get_db_session)],
    account: Annotated[UserAccount, Depends(require_roles(UserRole.SUPER_ADMIN))],
) -> ImportResponse:
    if payload.batch_id is not None:
        batch = db.get(PersonnelImportBatch, payload.batch_id)
        if batch is None or batch.status not in {"ready", "ready_with_warning"}:
            raise HTTPException(status_code=404, detail="Import batch is not ready")
        rows = list(db.scalars(select(PersonnelImportRow).where(PersonnelImportRow.batch_id == batch.id).order_by(PersonnelImportRow.row_number)))
        records = [EmployeeImportRecord(**json.loads(row.raw_data_text)) for row in rows if row.validation_status == "valid"]
        result = _apply_records(db, records, batch.filename, account.person_id, [])
        batch.status = "applied"
        batch.applied_at = __import__("backend.app.db.base", fromlist=["utc_now"]).utc_now()
        batch.added_count, batch.changed_count, batch.missing_count = result.added_count, result.changed_count, result.missing_count
        db.commit()
        result.batch_id = str(batch.id)
        return result
    if not payload.filename or not payload.content:
        raise HTTPException(status_code=422, detail="batch_id or filename/content is required")
    return import_snapshot(ImportRequest(filename=payload.filename, content=payload.content), db, account)
