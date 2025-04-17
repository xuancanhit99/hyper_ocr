import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Receipt splitter Service"
    PORT: int = int(os.getenv("PORT", 8000))
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for splittig receipt"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    

settings = Settings()