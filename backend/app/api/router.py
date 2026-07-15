from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.personnel import router as personnel_router
from backend.app.api.v1.practice_exam import router as practice_exam_router
from backend.app.api.v1.public_config import router as public_config_router
from backend.app.api.v1.question_authoring import router as question_authoring_router
from backend.app.api.v1.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(public_config_router)
api_router.include_router(practice_exam_router)
api_router.include_router(personnel_router)
api_router.include_router(reports_router)
api_router.include_router(question_authoring_router)
