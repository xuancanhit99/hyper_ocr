from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError, PermissionDenied, ResourceExhausted, InvalidArgument
import io
import logging
from typing import Dict, Any

# Import the response schema
from app.models.schemas import OCRResponse, BoundingBoxDetail, Vertex

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudVisionService:
    """
    Service class to interact with the Google Cloud Vision API for OCR tasks.
    """
    def __init__(self):
        """
        Initializes the Google Cloud Vision client.
        Credentials should be handled automatically via the GOOGLE_APPLICATION_CREDENTIALS env var.
        """
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Cloud Vision client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Vision client: {e}", exc_info=True)
            # Depending on requirements, you might want to raise the exception
            # or handle it such that the service reports unhealthy status.
            self.client = None # Ensure client is None if initialization fails

    async def detect_text(self, image_content: bytes) -> OCRResponse:
        """
        Performs text detection on the provided image content using Google Cloud Vision API.

        Args:
            image_content: The raw byte content of the image file.

        Returns:
            An OCRResponse object containing the extracted text and details.

        Raises:
            PermissionDenied: If the API key/credentials are invalid or lack permissions.
            ResourceExhausted: If the API quota has been exceeded.
            InvalidArgument: If the image format is invalid or corrupted.
            GoogleAPIError: For other Google Cloud API related errors.
            Exception: For unexpected errors during processing.
        """
        if not self.client:
             raise GoogleAPIError("Google Cloud Vision client is not initialized.")

        image = vision.Image(content=image_content)
        logger.info(f"Performing text detection on image of size: {len(image_content)} bytes")

        try:
            response = self.client.text_detection(image=image)
            logger.info("Received response from Google Cloud Vision API.")

            # Check for errors reported in the response object itself
            if response.error.message:
                logger.error(f"Google Cloud Vision API returned an error: {response.error.message}")
                # Map Google's error to a specific exception type if desired, or raise a generic one
                raise GoogleAPIError(f"Error in text recognition: {response.error.message}")

        except PermissionDenied as e:
            logger.error(f"Permission denied error from Google Cloud Vision: {e}", exc_info=True)
            raise PermissionDenied(f"Permission denied: Check credentials/API key permissions. Original error: {e}")
        except ResourceExhausted as e:
            logger.error(f"Resource exhausted error from Google Cloud Vision: {e}", exc_info=True)
            raise ResourceExhausted(f"API quota exceeded. Original error: {e}")
        except InvalidArgument as e:
            logger.error(f"Invalid argument error from Google Cloud Vision: {e}", exc_info=True)
            raise InvalidArgument(f"Invalid image format or content. Original error: {e}")
        except GoogleAPIError as e:
            logger.error(f"Google API error during text detection: {e}", exc_info=True)
            raise GoogleAPIError(f"A Google Cloud API error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during text detection: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred: {e}") # Re-raise generic exception

        texts = response.text_annotations
        if not texts:
            logger.info("No text detected in the image.")
            return OCRResponse(text="", details=[])

        # Process the results into the Pydantic schema format
        full_text = texts[0].description
        details = []

        # Start from index 1 to skip the full text annotation
        for text_annotation in texts[1:]:
            vertices = [Vertex(x=v.x, y=v.y) for v in text_annotation.bounding_poly.vertices]
            details.append(BoundingBoxDetail(
                text=text_annotation.description,
                bounding_box=vertices
            ))

        logger.info(f"Text detection successful. Full text length: {len(full_text)}, Details count: {len(details)}")
        return OCRResponse(text=full_text, details=details)