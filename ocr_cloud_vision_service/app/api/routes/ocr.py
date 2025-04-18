from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

# Import the service and schema
from app.services.ocr_service import CloudVisionService
from app.models.schemas import OCRResponse

# Import specific exceptions from Google API Core and the service
from google.api_core.exceptions import GoogleAPIError, PermissionDenied, ResourceExhausted, InvalidArgument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the router for OCR endpoints
router = APIRouter(
    prefix="/ocr",  # Prefix for all routes in this file
    tags=["OCR"]    # Tag for OpenAPI documentation
)

# Instantiate the service (consider dependency injection for better testability if needed)
# For simplicity here, we instantiate directly.
ocr_service = CloudVisionService()

@router.post(
    "/extract-text", # Renamed endpoint path
    response_model=OCRResponse, # Define the expected response structure
    summary="Extract text from an uploaded image using Google Cloud Vision" # Updated summary slightly
)
async def detect_text_from_image(
    file: UploadFile = File(..., description="Image file to perform OCR on.")
):
    """
    Receives an uploaded image file, performs OCR using Google Cloud Vision,
    and returns the extracted text along with bounding box details.

    - **file**: The image file (e.g., JPEG, PNG).
    """
    # Basic validation for content type
    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning(f"Invalid file content type received: {file.content_type}")
        raise HTTPException(status_code=400, detail=f"File must be an image (received type: {file.content_type})")

    logger.info(f"Received file '{file.filename}' with content type '{file.content_type}' for OCR.")

    try:
        # Read the file content as bytes
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from file '{file.filename}'.")

        # Call the OCR service method
        result = await ocr_service.detect_text(contents)
        logger.info(f"Successfully processed file '{file.filename}'.")
        return result

    # Handle specific exceptions raised by the service layer
    except PermissionDenied as e:
        logger.error(f"Permission denied error processing '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=403, detail=str(e)) # Forbidden
    except ResourceExhausted as e:
        logger.error(f"Resource exhausted error processing '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=429, detail=str(e)) # Too Many Requests
    except InvalidArgument as e:
        logger.error(f"Invalid argument error processing '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) # Bad Request
    except GoogleAPIError as e:
        logger.error(f"Google API error processing '{file.filename}': {e}", exc_info=True)
        # Use 502 Bad Gateway as suggested in reference for upstream errors
        raise HTTPException(status_code=502, detail=f"Upstream Google API Error: {e}")
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error processing '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
    finally:
        # Ensure the file is closed, although FastAPI handles this with UploadFile context
        await file.close()