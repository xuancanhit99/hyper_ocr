import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    PROJECT_NAME: str = "OCR Cloud Vision Service"
    API_V1_STR: str = "" # Remove API prefix for consistency

    # Google Cloud Vision configuration
    # GOOGLE_APPLICATION_CREDENTIALS is read directly by the google-cloud library
    # No need to explicitly define it here unless used for other purposes.

    # Service Port (optional, defaults if not set)
    PORT: int = int(os.getenv("PORT", 8810))

    # Allow all origins for CORS in this example, adjust as needed for production
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        # Makes BaseSettings case-insensitive for environment variables
        case_sensitive = False
        # Specifies the .env file to load (optional)
        # env_file = ".env"

# Create a single instance of the settings to be imported elsewhere
settings = Settings()