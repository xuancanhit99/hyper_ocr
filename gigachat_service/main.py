import uvicorn
from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from app.api.routes import chat, health # Import health router
from app.core.config import settings, logger

# Define lifespan events if needed (e.g., for startup/shutdown tasks)
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Code to run on startup
#     logger.info("GigaChat Service starting up...")
#     yield
#     # Code to run on shutdown
#     logger.info("GigaChat Service shutting down...")

# Create FastAPI app instance
# app = FastAPI(title="GigaChat Service", version="1.0.0", lifespan=lifespan)
app = FastAPI(title="GigaChat Service", version="1.0.0")


# Include routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(health.router, tags=["Health"]) # Include health router

# Entry point for running the application directly (e.g., for local development)
if __name__ == "__main__":
    logger.info(f"Starting GigaChat Service on port {settings.APP_PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True, # Enable reload for development convenience
        log_level=settings.LOG_LEVEL.lower()
    )