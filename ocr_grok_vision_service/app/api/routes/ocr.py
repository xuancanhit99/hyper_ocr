# app/api/routes/ocr.py
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    status,
    Depends,
    Form,
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
    summary="Perform OCR on an Image using Grok Vision API",
    description=(
        "Upload an image file (JPEG or PNG) to extract text using the "
        "configured Grok vision model. Specify an alternative model via 'model_name'."
    ),
    tags=["OCR"],
    responses={
        status.HTTP_200_OK: {"model": OCRResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorDetail},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorDetail},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorDetail},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ErrorDetail},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorDetail},
        status.HTTP_502_BAD_GATEWAY: {"model": ErrorDetail},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorDetail},
        status.HTTP_504_GATEWAY_TIMEOUT: {"model": ErrorDetail},
    }
)
async def perform_ocr(
    service: Annotated[OCRService, Depends(get_ocr_service)],
        file: UploadFile = File(..., description=f"Image file (JPEG or PNG)."),
    model_name: str | None = Form(None, description=f"Optional: Specify Grok vision model. Defaults to '{settings.GROK_DEFAULT_MODEL}'.")
):
    """
    Receives an image file (JPEG/PNG), sends it to the OCR service,
    and returns the extracted text.
    """
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No upload file sent.")

    guessed_type = None
    if file.content_type not in ALLOWED_CONTENT_TYPES:
         guessed_type, _ = mimetypes.guess_type(file.filename or "")
         if guessed_type not in ALLOWED_CONTENT_TYPES:
            # Removed logger.warning
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: '{file.content_type or guessed_type}'. Only JPEG and PNG are supported."
            )


    try:
        extracted_text, model_used = await service.extract_text_from_image(file, model_name)
        return OCRResponse(
            filename=file.filename or "uploaded_image",
            text=extracted_text,
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
