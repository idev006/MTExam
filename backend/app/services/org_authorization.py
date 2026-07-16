"""Organization-scope authorization shared by content and exam endpoints."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import OrgUnit, PersonUnitAssignment, UserAccount
from backend.app.domain.enums import UserRole


def active_org_unit_ids(db: Session, account: UserAccount) -> set[UUID]:
    if account.role == UserRole.SUPER_ADMIN:
        return set(db.scalars(select(OrgUnit.id).where(OrgUnit.status == "active")))
    today = date.today()
    return set(
        db.scalars(
            select(PersonUnitAssignment.org_unit_id)
            .join(OrgUnit, OrgUnit.id == PersonUnitAssignment.org_unit_id)
            .where(
                PersonUnitAssignment.person_id == account.person_id,
                PersonUnitAssignment.effective_from <= today,
                (PersonUnitAssignment.effective_to.is_(None))
                | (PersonUnitAssignment.effective_to >= today),
                OrgUnit.status == "active",
            )
        )
    )


def can_access_org_unit(db: Session, account: UserAccount, org_unit_id: UUID) -> bool:
    return account.role == UserRole.SUPER_ADMIN or org_unit_id in active_org_unit_ids(db, account)
