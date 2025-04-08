# app/main.py
from fastapi import FastAPI
from app.api.routes import ocr, health, chat # Import the new chat router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    # docs_url="/docs", # Uncomment if needed
    # redoc_url="/redoc", # Uncomment if needed
)

app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"]) # Include the chat router


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
    import uvicorn

    print(f"Starting server. Access API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # reload=True tự động cập nhật khi thay đổi mã - chỉ dùng cho môi trường phát triển
