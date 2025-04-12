import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Russian Receipt OCR Service"
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # OCR settings
    PYTESSERACT_PATH: str = os.getenv("PYTESSERACT_PATH", "/usr/bin/tesseract")
    
    
    class Config:
        env_file = ".env"

settings = Settings()