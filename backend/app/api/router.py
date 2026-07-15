from fastapi import APIRouter

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.practice_exam import router as practice_exam_router
from backend.app.api.v1.public_config import router as public_config_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(public_config_router)
api_router.include_router(practice_exam_router)
