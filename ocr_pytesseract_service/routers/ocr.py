# routers/ocr.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.ocr_services import extract_text_from_image, parse_receipt_data
from typing import Optional
import logging

router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.post("/receipt")
async def process_receipt(
    image: UploadFile = File(...),
):
    """
    Process a receipt image and extract the relevant information
    """
    try:
        # Extract text from image using OCR
        extracted_text = await extract_text_from_image(image)
        
        # Parse the extracted text to get receipt data
        receipt_data = parse_receipt_data(extracted_text)
        
        return receipt_data
    
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process receipt: {str(e)}"
        )