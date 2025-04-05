# app/models/schemas.py
from pydantic import BaseModel, Field

class OCRResponse(BaseModel):
    filename: str = Field(..., description="Original filename of the uploaded image.")
    content_type: str = Field(..., description="MIME type of the uploaded file.")
    extracted_text: str = Field(..., description="Text extracted from the image by the Grok model.")
    model_used: str = Field(..., description="The specific Grok model used for OCR.")

class HealthResponse(BaseModel):
    status: str = Field("ok", description="Indicates the health status of the service.")
    app_name: str = Field(..., description="Name of the application.")
    app_version: str = Field(..., description="Version of the application.")

class ErrorDetail(BaseModel):
    detail: str = Field(..., description="A detailed message describing the error.")