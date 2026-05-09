from fastapi import APIRouter
from .scan import router as scan_router
from .reports import router as reports_router
from .feedback import router as feedback_router
from .users import router as users_router
from .health import router as health_router

api_router = APIRouter()

api_router.include_router(scan_router, prefix="/v1", tags=["scan"])
api_router.include_router(reports_router, prefix="/v1", tags=["reports"])
api_router.include_router(feedback_router, prefix="/v1", tags=["feedback"])
api_router.include_router(users_router, prefix="/v1", tags=["users"])
api_router.include_router(health_router, prefix="/v1", tags=["health"])

__all__ = ["api_router"]
