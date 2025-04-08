# app/api/routes/ocr.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Header, Depends, Query
from typing import Annotated # Import Annotated
from app.models.schemas import OCRResponse, ErrorResponse
from app.services.gemini import GeminiService
from app.core.config import get_settings
from PIL import Image
import io

router = APIRouter()
settings = get_settings()
# Remove global instance: gemini_service = GeminiService()

# Dependency function
def get_gemini_service(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    model_name: str | None = Query(None, description="Optional: Specify Gemini model name") # Use Query for model_name
) -> GeminiService:
    try:
        return GeminiService(api_key=x_api_key, model_name=model_name)
    except ValueError as e:
        # Handle initialization errors (e.g., missing API key if not provided in header and not in .env)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Gemini Service initialization failed: {e}"
        )


@router.post(
    "/extract-text",
    response_model=OCRResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    }
)
async def extract_text_from_image(
        service: Annotated[GeminiService, Depends(get_gemini_service)], # Inject service
        file: UploadFile = File(..., description="Image file to process"),
        prompt: str | None = Query(None, description="Optional: Custom prompt for OCR extraction") # Use Query for prompt
        # model_name and x_api_key are now handled by Depends(get_gemini_service)
):
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_CONTENT_TYPES)}"
        )

    try:
        # Service is now injected, no need to create it here
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()

        extracted_text = await service.extract_text(
            image_bytes,
            file.content_type,
            prompt=prompt
        )

        return OCRResponse(
            filename=file.filename,
            content_type=file.content_type,
            extracted_text=extracted_text,
            model_used=service.model_name # Get model_name from the injected service
        )
    finally:
        await file.close()