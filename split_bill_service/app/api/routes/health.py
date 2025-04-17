# app/api/routes/health.py
from fastapi import APIRouter, status

from pydantic import BaseModel
from datetime import datetime
import psutil
import time

from app.services.split_services import split_by_dishes, split_equal_by_names, split_by_percent

router = APIRouter()
start_time = time.time()

class HealthResponse(BaseModel):
    status: str
    uptime: str
    system_stats: dict

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():

    try:
        service_1 = split_by_dishes()
        service_2 = split_equal_by_names()
        service_3 = split_by_percent()
        status = True
    except Exception:
        status = False

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
        system_stats=system_stats
    )