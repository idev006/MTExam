"""Generate a device acceptance checklist for human/browser execution."""

from __future__ import annotations

import json

DEVICES = {
    "smartphone": [(390, 844), (412, 915)],
    "tablet": [(768, 1024), (1024, 1366)],
    "notebook": [(1366, 768), (1440, 900)],
    "pc": [(1920, 1080), (2560, 1440)],
}
WORKFLOWS = ["login", "dashboard", "exam", "autosave-recovery", "submit-result", "admin-scope"]


def main() -> None:
    rows = [
        {"device": device, "viewport": viewport, "workflow": workflow, "passed": False}
        for device, viewports in DEVICES.items()
        for viewport in viewports
        for workflow in WORKFLOWS
    ]
    print(
        json.dumps(
            {"status": "human_acceptance_required", "cases": rows},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
