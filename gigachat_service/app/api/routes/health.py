from fastapi import APIRouter, status
from app.core.config import logger

router = APIRouter()

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the GigaChat service is running and operational.",
    tags=["Health"]
)
async def health_check():
    """
    Simple health check endpoint. Returns HTTP 200 OK if the service is running.
    """
    logger.debug("Health check endpoint called")
    # In the future, more comprehensive checks could be added here (e.g., check GigaChat connectivity)
    return {"status": "ok", "service": "GigaChat Service"}