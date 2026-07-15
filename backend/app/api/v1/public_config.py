from fastapi import APIRouter, Request

from backend.app.api.schemas import PublicConfigResponse

router = APIRouter(tags=["system"])


@router.get("/public-config", response_model=PublicConfigResponse)
def get_public_config(request: Request) -> PublicConfigResponse:
    settings = request.app.state.settings
    return PublicConfigResponse(
        app_name=settings.app.name,
        api_version=settings.app.version,
        maximum_upload_size_mb=settings.personnel_import.maximum_file_size_mb,
        show_result_after_submit=settings.exam.show_result_after_submit,
        allow_late_entry=settings.exam.batch.allow_late_entry,
    )
