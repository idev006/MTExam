from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from faker import Faker


def build_demo_employees(count: int = 25, seed: int = 20260715) -> list[dict[str, Any]]:
    """Build deterministic employee-shaped data without touching the database."""
    if count < 0:
        raise ValueError("count must be non-negative")

    fake = Faker("th_TH")
    fake.seed_instance(seed)
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    ranks = ("พ.ต.อ.", "พ.ต.ท.", "ร.ต.อ.", "ด.ต.", "ส.ต.อ.")
    positions = ("ผู้กำกับการ", "รองผู้กำกับการ", "สารวัตร", "รองสารวัตร", "ผู้บังคับหมู่")
    units = ("กก.1 บก.น.6", "กก.2 บก.น.6", "กก.3 บก.น.6")

    return [
        {
            "emp_cid": fake.numerify("#############"),
            "emp_yod": ranks[index % len(ranks)],
            "emp_fname": fake.first_name(),
            "emp_lname": fake.last_name(),
            "emp_position": positions[index % len(positions)],
            "emp_position_rank": (len(positions) - index % len(positions)) * 10,
            "emp_yod_rank": (len(ranks) - index % len(ranks)) * 10,
            "emp_gender": fake.random_element(elements=("ชาย", "หญิง")),
            "emp_tel": fake.numerify("08########"),
            "emp_bh": "บช.น.",
            "emp_bk": "บก.น.6",
            "emp_kk": units[index % len(units)],
            "emp_status": "active" if index % 7 else "changed",
            "emp_descr": "ข้อมูลจำลองสำหรับการพัฒนา" if index % 5 == 0 else None,
            "created_dt": now,
            "updated_dt": now,
        }
        for index in range(count)
    ]
