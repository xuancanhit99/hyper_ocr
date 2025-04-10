import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import settings and routers
from app.core.config import settings
from app.api.routes import health, ocr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json", # Standard OpenAPI doc path - Removed prefix
    openapi_url="/openapi.json", # Set default OpenAPI path
    version="1.0.0" # Add a version number
)

# Configure CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS], # Ensure origins are strings
        allow_credentials=True,
        allow_methods=["*"], # Allow all standard methods
        allow_headers=["*"], # Allow all headers
    )
    logger.info(f"CORS middleware enabled for origins: {settings.CORS_ORIGINS}")
else:
    logger.info("CORS middleware disabled (no origins specified in settings).")


# Include API routers
# Health check endpoint (no prefix needed as it's defined in the router)
app.include_router(health.router)
# OCR endpoints (prefix defined in settings)
app.include_router(ocr.router, prefix=settings.API_V1_STR)

logger.info(f"Included health router at /health")
# Log the included router path (prefix is now empty, path comes from ocr.router)
logger.info(f"Included OCR router at /ocr")


# Root endpoint (optional, good for basic check)
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint providing basic service information.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# Main entry point for running the application directly (e.g., for local testing)
if __name__ == "__main__":
    logger.info(f"Starting Uvicorn server on host 0.0.0.0, port {settings.PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False # Set reload=True only for development
    )