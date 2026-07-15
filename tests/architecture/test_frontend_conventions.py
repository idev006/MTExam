import re
from pathlib import Path

FRONTEND_SRC = Path(__file__).parents[2] / "frontend" / "src"


def test_frontend_uses_reusable_feedback_and_page_template() -> None:
    source_files = list(FRONTEND_SRC.rglob("*.vue")) + list(FRONTEND_SRC.rglob("*.ts"))
    combined = "\n".join(path.read_text(encoding="utf-8") for path in source_files)

    assert not re.search(r"window\.(alert|confirm|prompt)\s*\(", combined)
    for relative_path in (
        "components/layout/PageContainer.vue",
        "components/layout/PageHeader.vue",
        "components/feedback/AppAlert.vue",
        "components/feedback/AppToast.vue",
        "components/feedback/ConfirmModal.vue",
        "stores/theme.ts",
    ):
        assert (FRONTEND_SRC / relative_path).is_file(), relative_path
