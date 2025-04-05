# app/api/routes/health.py
from fastapi import APIRouter, status

from pydantic import BaseModel
from datetime import datetime
import psutil
import time

from app.services.ocr_service import OCRService

router = APIRouter()
start_time = time.time()

class HealthResponse(BaseModel):
    status: str
    uptime: str
    xai_api: bool
    system_stats: dict

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    # Check XAI API connection
    try:
        grok_service = OCRService()
        xai_status = True
    except Exception:
        xai_status = False

    # Calculate uptime
    uptime = str(datetime.fromtimestamp(time.time() - start_time).strftime('%H:%M:%S'))

    # Get system stats
    system_stats = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

    return HealthResponse(
        status="healthy",
        uptime=uptime,
        xai_api=xai_status,
        system_stats=system_stats
    )