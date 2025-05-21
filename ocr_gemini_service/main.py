# app/main.py
from fastapi import FastAPI
from app.api.routes import ocr, health, chat # Import the new chat router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.include_router(ocr.router, prefix="/vision", tags=["OCR"])
app.include_router(health.router, tags=["Health"]) # Add tag for consistency
app.include_router(chat.router, prefix="/chat", tags=["Chat"]) # Include the chat router
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}!"}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server. Access API docs at http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # reload=True tự động cập nhật khi thay đổi mã - chỉ dùng cho môi trường phát triển