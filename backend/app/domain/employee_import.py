from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields

from backend.app.domain.enums import ImportAction

EMPLOYEE_INPUT_FIELDS = (
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
)
REQUIRED_INPUT_FIELDS = frozenset({"emp_cid", "emp_fname", "emp_lname", "emp_status"})
RANK_FIELDS = frozenset({"emp_position_rank", "emp_yod_rank"})
ORG_FIELDS = frozenset({"emp_bh", "emp_bk", "emp_kk"})
CID_PATTERN = re.compile(r"^[0-9]{13}$")


class EmployeeCsvSchemaError(ValueError):
    """A fatal CSV problem that prevents reliable row parsing."""


@dataclass(frozen=True, slots=True)
class EmployeeImportRecord:
    emp_cid: str
    emp_yod: str | None
    emp_fname: str
    emp_lname: str
    emp_position: str | None
    emp_position_rank: int | None
    emp_yod_rank: int | None
    emp_gender: str | None
    emp_tel: str | None
    emp_bh: str | None
    emp_bk: str | None
    emp_kk: str | None
    emp_status: str
    emp_descr: str | None


@dataclass(frozen=True, slots=True)
class EmployeeRowError:
    row_number: int
    field: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class EmployeeParseResult:
    records: tuple[EmployeeImportRecord, ...]
    errors: tuple[EmployeeRowError, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True, slots=True)
class EmployeeReconciliation:
    emp_cid: str
    action: ImportAction
    changed_fields: tuple[str, ...] = ()


def parse_employee_csv(
    payload: bytes,
    *,
    header_map: Mapping[str, str] | None = None,
    encoding: str = "utf-8-sig",
    delimiter: str = ",",
) -> EmployeeParseResult:
    """Parse a full-snapshot CSV without changing persistent data."""

    resolved_headers = _resolve_headers(header_map)
    try:
        content = payload.decode(encoding)
    except (LookupError, UnicodeDecodeError) as exc:
        raise EmployeeCsvSchemaError("CSV must use the configured UTF-8 encoding") from exc

    reader = csv.DictReader(io.StringIO(content, newline=""), delimiter=delimiter)
    _validate_headers(reader.fieldnames, resolved_headers)

    records: list[EmployeeImportRecord] = []
    errors: list[EmployeeRowError] = []
    first_row_by_cid: dict[str, int] = {}
    for row_number, source_row in enumerate(reader, start=2):
        normalized = {
            canonical: _normalize_text(source_row.get(source_header))
            for canonical, source_header in resolved_headers.items()
        }
        row_errors = _validate_row(normalized, row_number)
        cid = normalized["emp_cid"]
        if cid:
            if cid in first_row_by_cid:
                row_errors.append(
                    EmployeeRowError(
                        row_number=row_number,
                        field="emp_cid",
                        code="duplicate_identifier",
                        message="Identifier already appeared in this file",
                    )
                )
            else:
                first_row_by_cid[cid] = row_number

        if row_errors:
            errors.extend(row_errors)
            continue
        records.append(_build_record(normalized))

    return EmployeeParseResult(records=tuple(records), errors=tuple(errors))


def reconcile_employee_snapshot(
    current: Iterable[EmployeeImportRecord],
    incoming: Iterable[EmployeeImportRecord],
) -> tuple[EmployeeReconciliation, ...]:
    """Classify a validated full snapshot deterministically by stable identifier."""

    current_by_cid = _index_unique(current, source="current")
    incoming_by_cid = _index_unique(incoming, source="incoming")
    result: list[EmployeeReconciliation] = []

    for cid in sorted(current_by_cid.keys() | incoming_by_cid.keys()):
        before = current_by_cid.get(cid)
        after = incoming_by_cid.get(cid)
        if before is None:
            result.append(EmployeeReconciliation(cid, ImportAction.ADDED))
            continue
        if after is None:
            result.append(EmployeeReconciliation(cid, ImportAction.MISSING))
            continue

        changed = _changed_fields(before, after)
        if not changed:
            action = ImportAction.UNCHANGED
        elif before.emp_status != "active" and after.emp_status == "active":
            action = ImportAction.REACTIVATE
        elif ORG_FIELDS.intersection(changed):
            action = ImportAction.MOVED
        else:
            action = ImportAction.CHANGED
        result.append(EmployeeReconciliation(cid, action, changed))

    return tuple(result)


def _resolve_headers(header_map: Mapping[str, str] | None) -> dict[str, str]:
    resolved = dict(header_map or {name: name for name in EMPLOYEE_INPUT_FIELDS})
    missing_mappings = set(EMPLOYEE_INPUT_FIELDS) - resolved.keys()
    if missing_mappings:
        joined = ", ".join(sorted(missing_mappings))
        raise EmployeeCsvSchemaError(f"Header mapping is missing canonical fields: {joined}")
    return {name: resolved[name] for name in EMPLOYEE_INPUT_FIELDS}


def _validate_headers(fieldnames: list[str] | None, header_map: Mapping[str, str]) -> None:
    if fieldnames is None:
        raise EmployeeCsvSchemaError("CSV header is missing")
    if len(fieldnames) != len(set(fieldnames)):
        raise EmployeeCsvSchemaError("CSV header contains duplicate columns")
    required_headers = {header_map[name] for name in REQUIRED_INPUT_FIELDS}
    missing = required_headers - set(fieldnames)
    if missing:
        joined = ", ".join(sorted(missing))
        raise EmployeeCsvSchemaError(f"CSV is missing required headers: {joined}")


def _validate_row(row: Mapping[str, str | None], row_number: int) -> list[EmployeeRowError]:
    errors: list[EmployeeRowError] = []
    for field_name in sorted(REQUIRED_INPUT_FIELDS):
        if not row[field_name]:
            errors.append(
                EmployeeRowError(
                    row_number=row_number,
                    field=field_name,
                    code="required",
                    message="Required value is missing",
                )
            )

    cid = row["emp_cid"]
    if cid and not CID_PATTERN.fullmatch(cid):
        errors.append(
            EmployeeRowError(
                row_number=row_number,
                field="emp_cid",
                code="invalid_identifier_format",
                message="Identifier must contain exactly 13 digits",
            )
        )

    for field_name in sorted(RANK_FIELDS):
        value = row[field_name]
        if value is None:
            continue
        try:
            parsed = int(value)
        except ValueError:
            code = "invalid_integer"
            message = "Rank must be an integer"
        else:
            if parsed >= 0:
                continue
            code = "negative_rank"
            message = "Rank must not be negative"
        errors.append(
            EmployeeRowError(
                row_number=row_number,
                field=field_name,
                code=code,
                message=message,
            )
        )
    return errors


def _build_record(row: Mapping[str, str | None]) -> EmployeeImportRecord:
    return EmployeeImportRecord(
        emp_cid=str(row["emp_cid"]),
        emp_yod=row["emp_yod"],
        emp_fname=str(row["emp_fname"]),
        emp_lname=str(row["emp_lname"]),
        emp_position=row["emp_position"],
        emp_position_rank=_parse_optional_integer(row["emp_position_rank"]),
        emp_yod_rank=_parse_optional_integer(row["emp_yod_rank"]),
        emp_gender=row["emp_gender"],
        emp_tel=row["emp_tel"],
        emp_bh=row["emp_bh"],
        emp_bk=row["emp_bk"],
        emp_kk=row["emp_kk"],
        emp_status=str(row["emp_status"]),
        emp_descr=row["emp_descr"],
    )


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _parse_optional_integer(value: str | None) -> int | None:
    return int(value) if value is not None else None


def _index_unique(
    records: Iterable[EmployeeImportRecord],
    *,
    source: str,
) -> dict[str, EmployeeImportRecord]:
    indexed: dict[str, EmployeeImportRecord] = {}
    for record in records:
        if record.emp_cid in indexed:
            raise ValueError(f"Duplicate identifier in {source} records")
        indexed[record.emp_cid] = record
    return indexed


def _changed_fields(
    before: EmployeeImportRecord,
    after: EmployeeImportRecord,
) -> tuple[str, ...]:
    comparable_fields = (
        field.name for field in fields(EmployeeImportRecord) if field.name != "emp_cid"
    )
    return tuple(
        field_name
        for field_name in comparable_fields
        if getattr(before, field_name) != getattr(after, field_name)
    )
