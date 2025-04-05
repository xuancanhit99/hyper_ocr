# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "OCR Grok Vision Service"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Using Grok Vision Models to Extract Text from Images"

    XAI_API_KEY: str = os.getenv("XAI_API_KEY")
    XAI_API_BASE_URL: str = "https://api.x.ai/v1"
    GROK_DEFAULT_MODEL: str =  os.getenv("GROK_DEFAULT_MODEL", "grok-2-vision-1212")

@lru_cache()
def get_settings():
    return Settings()