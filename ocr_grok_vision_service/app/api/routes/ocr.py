# app/api/routes/ocr.py
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    status,
    Depends,
    Header,
    Query
)
from app.services.ocr_service import OCRService
from app.models.schemas import OCRResponse, ErrorDetail
from app.core.config import get_settings, Settings
from typing import Annotated
import mimetypes # Keep for MIME type guessing

router = APIRouter()

settings = get_settings()

def get_ocr_service():
    try:
        return OCRService()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OCR Service initialization failed: {e}"
        )

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]

@router.post(
    "/extract-text",
    response_model=OCRResponse,
    summary="Perform OCR on an Image using Grok Vision API"
)
async def perform_ocr(
    service: Annotated[OCRService, Depends(get_ocr_service)],
    file: UploadFile = File(..., description="Image file (JPEG or PNG)."),
    model_name: str | None = Query(None, description=f"Optional: Specify Grok vision model."),
    prompt: str | None = Query(
        None,
        description="Custom prompt for OCR extraction"
    ),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
):
    """
    Receives an image file (JPEG/PNG), sends it to the OCR service,
    and returns the extracted text.
    """
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No upload file sent.")

    # Check file type
    guessed_type = None
    if file.content_type not in ALLOWED_CONTENT_TYPES:
         guessed_type, _ = mimetypes.guess_type(file.filename or "")
         if guessed_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: '{file.content_type or guessed_type}'. Only JPEG and PNG are supported."
            )

    try:
        extracted_text, model_used = await service.extract_text_from_image(
            file,
            model_name=model_name,
            prompt=prompt,
            api_key=x_api_key
        )
        content_type = file.content_type
        if content_type not in ALLOWED_CONTENT_TYPES:
            guessed_type, _ = mimetypes.guess_type(file.filename or "")
            if guessed_type in ALLOWED_CONTENT_TYPES:
                content_type = guessed_type
            else:
                content_type = "image/unknown"

        return OCRResponse(
            filename=file.filename or "uploaded_image",
            content_type=content_type,
            extracted_text=extracted_text,
            model_used=model_used
        )
    except HTTPException as http_exc:
         raise http_exc
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred in the API processing layer."
        ) from e
    finally:
        await file.close()

