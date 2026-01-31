from fastapi import APIRouter
from datetime import datetime

from ..config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/status")
async def status():
    return {
        "companies_tracked": 0,
        "last_scoring_run": None,
        "macro_data_updated": None,
    }
