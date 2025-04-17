from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import split, health
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(split.router, prefix="/split", tags=["Split"])
app.include_router(health.router, tags = ["Health"])

@app.get("/", tags=["Root"], summary="Root Endpoint")
async def root():
    """Provides basic information about the service."""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "documentation": "/docs"
        
    }

if __name__ == "__main__":
    print(f"Starting server. Access API docs at http://0.0.0.0:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)