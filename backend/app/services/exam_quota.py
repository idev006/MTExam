"""Resolve and enforce per-organization Exam Creation quotas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import (
    ExamPaperOrgUnit,
    ExamSession,
    ExamWindow,
    ExamWindowScope,
    OrgUnit,
    PersonUnitAssignment,
    UserAccount,
)
from backend.app.domain.enums import UserRole


def _ancestor_ids(db: Session, org_unit_id: UUID) -> list[UUID]:
    result = [org_unit_id]
    unit = db.get(OrgUnit, org_unit_id)
    while unit and unit.parent_id is not None:
        result.append(unit.parent_id)
        unit = db.get(OrgUnit, unit.parent_id)
    return result


def reserve_quota(
    db: Session,
    *,
    account: UserAccount,
    window: ExamWindow,
) -> tuple[UUID, UUID]:
    """Return (actual organization, quota organization) after a locked capacity check."""
    window_scope = set(
        db.scalars(
            select(ExamWindowScope.org_unit_id).where(ExamWindowScope.exam_window_id == window.id)
        )
    )
    quotas = list(
        db.scalars(
            select(ExamPaperOrgUnit).where(
                ExamPaperOrgUnit.exam_paper_id == window.exam_paper_id,
                ExamPaperOrgUnit.org_unit_id.in_(window_scope),
            )
        )
    )
    today = date.today()
    assignment_ids = list(
        db.scalars(
            select(PersonUnitAssignment.org_unit_id).where(
                PersonUnitAssignment.person_id == account.person_id,
                PersonUnitAssignment.effective_from <= today,
                (PersonUnitAssignment.effective_to.is_(None))
                | (PersonUnitAssignment.effective_to >= today),
            )
        )
    )
    matches: list[tuple[UUID, UUID]] = []
    for assignment_id in assignment_ids:
        ancestors = set(_ancestor_ids(db, assignment_id))
        matches.extend(
            (assignment_id, quota.org_unit_id) for quota in quotas if quota.org_unit_id in ancestors
        )
    if not matches and account.role == UserRole.SUPER_ADMIN and quotas:
        matches = [(quotas[0].org_unit_id, quotas[0].org_unit_id)]
    quota_ids = {quota_id for _, quota_id in matches}
    if not matches:
        raise HTTPException(status_code=403, detail="Your organization has no exam quota")
    if len(quota_ids) > 1:
        raise HTTPException(
            status_code=409, detail="Multiple organization quotas match this account"
        )
    quota_id = next(iter(quota_ids))
    level_rank = {"division": 1, "bureau": 2, "station": 3, "sub_unit": 4}

    def assignment_rank(value: UUID) -> int:
        unit = db.get(OrgUnit, value)
        return level_rank.get(unit.level if unit else "", 0)

    actual_id = max(
        (actual for actual, matched_quota in matches if matched_quota == quota_id),
        key=assignment_rank,
    )
    quota = db.scalar(
        select(ExamPaperOrgUnit)
        .where(
            ExamPaperOrgUnit.exam_paper_id == window.exam_paper_id,
            ExamPaperOrgUnit.org_unit_id == quota_id,
        )
        .with_for_update()
    )
    if quota is None or quota.eligible_count is None:
        raise HTTPException(status_code=409, detail="Exam quota is not configured")
    used = (
        db.scalar(
            select(func.count())
            .select_from(ExamSession)
            .where(
                ExamSession.exam_window_id == window.id,
                ExamSession.eligibility_org_unit_id == quota_id,
            )
        )
        or 0
    )
    if used >= quota.eligible_count:
        raise HTTPException(status_code=409, detail="Organization exam quota is full")
    return actual_id, quota_id
