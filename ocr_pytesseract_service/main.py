from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import ocr
from config import settings

app = FastAPI(
    title="Russian Receipt OCR Service",
    description="API for extracting receipt information from images using OCR",
    version="1.0.0"
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
app.include_router(ocr.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Russian Receipt OCR Service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)