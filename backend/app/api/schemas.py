from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    version: str
    database: str


class PublicConfigResponse(BaseModel):
    app_name: str
    api_version: str
    maximum_upload_size_mb: int
    show_result_after_submit: bool
    allow_late_entry: bool
