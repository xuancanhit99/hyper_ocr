# app/services/gemini.py
import google.generativeai as genai
from app.core.config import get_settings
from fastapi import HTTPException, status

settings = get_settings()


class GeminiService:
    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        try:
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {e}")

    async def extract_text(self, image_data: bytes, content_type: str):
        if not self.model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini model not initialized"
            )

        image_part = {
            "mime_type": content_type,
            "data": image_data
        }
        prompt = "Extract all visible text from this image. Returns only the text content."

        try:
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except genai.types.generation_types.BlockedPromptException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content blocked by Gemini safety filters: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing image: {e}"
            )