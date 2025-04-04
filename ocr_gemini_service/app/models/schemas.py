# app/models/schemas.py
from pydantic import BaseModel

class OCRResponse(BaseModel):
    filename: str
    content_type: str
    extracted_text: str
    model_used: str

class ErrorResponse(BaseModel):
    detail: str