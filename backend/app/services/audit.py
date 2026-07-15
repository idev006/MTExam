from __future__ import annotations

# ruff: noqa: E501
import json
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.db.models import AuditLog


def record_audit(
    db: Session,
    *,
    actor_person_id: UUID | None,
    event_type: str,
    subject_type: str,
    subject_id: UUID | None = None,
    metadata: dict[str, object] | None = None,
) -> AuditLog:
    event = AuditLog(actor_person_id=actor_person_id, event_type=event_type, subject_type=subject_type, subject_id=subject_id, metadata_text=json.dumps(metadata or {}, ensure_ascii=False))
    db.add(event)
    return event
