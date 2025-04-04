# app/api/routes/ocr.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.models.schemas import OCRResponse, ErrorResponse
from app.services.gemini import GeminiService
from app.core.config import get_settings
from PIL import Image
import io

router = APIRouter()
settings = get_settings()
gemini_service = GeminiService()


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
        file: UploadFile = File(..., description="Image file to process"),
        prompt: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None
):
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_CONTENT_TYPES)}"
        )

    try:
        service = GeminiService(api_key=api_key, model_name=model_name)
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
            model_used=service.model_name
        )
    finally:
        await file.close()