from sqlalchemy import select

from backend.app.config import Settings
from backend.app.db.base import Base
from backend.app.db.database import Database
from backend.app.db.models import OrgUnit
from backend.app.main import _seed_region6_org_units, _seed_region6_sub_units

EXPECTED_SUB_UNITS = {
    "BAG_อำนวยการ_ภ6": [
        "ฝ่ายอำนวยการ 1",
        "ฝ่ายอำนวยการ 2",
        "ฝ่ายอำนวยการ 3",
        "ฝ่ายอำนวยการ 4",
        "ฝ่ายอำนวยการ 5",
        "ฝ่ายอำนวยการ 6",
    ],
    "BSS_ภ6": [
        "ฝอ.บก.สส.ภ.6",
        "สืบสวน 1 บก.สส.ภ.6",
        "สืบสวน 2 บก.สส.ภ.6",
        "สืบสวน 3 บก.สส.ภ.6",
        "วิเคราะห์ข่าวฯ บก.สส.ภ.6",
        "ปพ.บก.สส.ภ.6",
        "กลุ่มงานสอบสวน บก.สส.ภ.6",
    ],
    "ศฝร_ภ6": [
        "ฝ่ายอำนวยการ",
        "ฝ่ายบริการนักศึกษา ( บศ)",
        "ฝ่ายปกครองแฝละการฝึก (ปค)",
        "กลุ่มอาจารย์ (กอจ)",
    ],
}


def test_region6_sub_unit_seed_matches_authoritative_document_and_is_idempotent() -> None:
    database = Database(
        Settings(database_url="sqlite:///:memory:", app_secret_key="region6-seed-test-secret")
    )
    Base.metadata.create_all(database.engine)

    with database.session() as db:
        for _ in range(2):
            _seed_region6_org_units(db)
            _seed_region6_sub_units(db)
            db.commit()

        for parent_code, expected_names in EXPECTED_SUB_UNITS.items():
            parent = db.scalar(select(OrgUnit).where(OrgUnit.code == parent_code))
            assert parent is not None
            children = list(
                db.scalars(
                    select(OrgUnit)
                    .where(OrgUnit.parent_id == parent.id)
                    .order_by(OrgUnit.name)
                )
            )
            assert sorted(child.name for child in children) == sorted(expected_names)
            assert {child.level for child in children} == {"sub_unit"}
            assert {child.status for child in children} == {"active"}

    database.dispose()
