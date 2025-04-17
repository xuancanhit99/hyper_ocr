# routers/ocr.py
from fastapi import APIRouter, HTTPException, status, Body
from app.services.split_services import split_by_dishes, split_equal_by_names, split_by_percent
import logging
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter(
    prefix="/split",
    tags=["SPLIT"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

class Split_by_dishes_Request(BaseModel):
    dishes: Dict[str, Dict[str, float]]
    prices: Dict[str, float]
    discount: float
    tax: float
    tip: float
    service_fee: float

@router.post("/split-by-dishes")
async def process_receipt(request: Split_by_dishes_Request):
    """
    Process a receipt splitting
    """
    try:
        dict_splited = await split_by_dishes(
            request.dishes, 
            request.prices, 
            request.discount, 
            request.tax, 
            request.tip, 
            request.service_fee
        )
        
        return dict_splited
    
    except Exception as e:
        logger.error(f"Error processing splitting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process splitting: {str(e)}"
        )

class Split_equal_Request(BaseModel):
    total_bill: float
    people_names : List
 
    
@router.post("/split-equal")
async def process_receipt(request: Split_equal_Request):
    """
    Process a receipt splitting
    """
    try:
        dict_splited = await split_equal_by_names(request.total_bill, request.people_names)
        
        return dict_splited
    
    except Exception as e:
        logger.error(f"Error processing splitting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process splitting: {str(e)}"
        )
    
class Split_by_percent_Request(BaseModel):
    total_bill: float
    percent : Dict[str, float]
 
    
@router.post("/split-by-percent")
async def process_receipt(request: Split_by_percent_Request):
    """
    Process a receipt splitting
    """
    try:
        dict_splited = await split_by_percent(request.total_bill, request.percent)
        
        return dict_splited
    
    except Exception as e:
        logger.error(f"Error processing splitting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process splitting: {str(e)}"
        )