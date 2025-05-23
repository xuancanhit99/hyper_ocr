# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "OCR Gemini Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Using Google Gemini Models to Extract Text from Images"

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_VISION_MODEL_NAME: str =  os.getenv("GEMINI_VISION_MODEL_NAME", "gemini-2.0-flash-exp-image-generation") # Renamed for clarity
    GEMINI_TEXT_MODEL_NAME: str = os.getenv("GEMINI_TEXT_MODEL_NAME", "gemini-2.5-pro-exp-03-25") # Default text model

    ALLOWED_CONTENT_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]

@lru_cache()
def get_settings():
    return Settings()