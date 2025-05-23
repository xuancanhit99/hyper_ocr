import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging
from functools import lru_cache # Import lru_cache

# Load environment variables from .env file
load_dotenv() # pydantic-settings can also load .env automatically

class Settings(BaseSettings):
    """Application settings."""
    GIGACHAT_AUTH_KEY: str
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    GIGACHAT_DEFAULT_MODEL: str = "GigaChat-Pro"
    GIGACHAT_TOKEN_URL: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    GIGACHAT_CHAT_URL: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    APP_PORT: int = 6363
    LOG_LEVEL: str = "INFO"

    class Config:
        # If using a .env file, BaseSettings will automatically load it.
        # Specify the path if it's not in the root directory relative to this file.
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from environment

# Function to get cached settings
@lru_cache()
def get_settings():
    """Get application settings with caching."""
    return Settings()

# Instantiate settings using the cached function
settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL.upper(),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Configuration loaded successfully.")
# Avoid logging sensitive keys in production
# logger.debug(f"Loaded settings: {settings.dict()}")