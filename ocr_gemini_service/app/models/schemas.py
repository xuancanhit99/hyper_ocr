# app/models/schemas.py
from pydantic import BaseModel


class OCRRequest(BaseModel):
    prompt: str | None = None
    model_name: str | None = None
    api_key: str | None = None


class OCRResponse(BaseModel):
    filename: str
    content_type: str
    extracted_text: str
    model_used: str


class ErrorResponse(BaseModel):
    detail: str
