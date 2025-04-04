# app/main.py
from fastapi import FastAPI
from app.api.routes import ocr
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}!"}