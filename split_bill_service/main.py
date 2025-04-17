from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import split
from app.core.config import settings

app = FastAPI(
    title="Receipt Splitter Service",
    description="API for splittig receipt",
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
app.include_router(split.router)

@app.get("/")
async def root():
    return {"message": "Receipt Splitter Service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)