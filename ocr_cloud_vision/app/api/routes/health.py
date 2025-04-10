from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health Check"], summary="Check service health")
async def health_check():
    """
    Simple health check endpoint to confirm the service is running.
    Returns a static JSON response.
    """
    return {"status": "ok"}