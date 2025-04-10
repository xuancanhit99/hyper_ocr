from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Vertex(BaseModel):
    """Represents a single vertex (corner point) of a bounding box."""
    x: int = Field(..., description="X-coordinate of the vertex.")
    y: int = Field(..., description="Y-coordinate of the vertex.")

class BoundingBoxDetail(BaseModel):
    """Represents the details of a detected text block, including its bounding box."""
    text: str = Field(..., description="The text detected within this bounding box.")
    bounding_box: List[Vertex] = Field(..., description="List of vertices defining the bounding polygon.")

class OCRResponse(BaseModel):
    """Defines the structure of the response for the OCR detection endpoint."""
    text: str = Field(..., description="The full text extracted from the image.")
    details: List[BoundingBoxDetail] = Field(..., description="Detailed information for each detected text block, including bounding boxes.")

# Example of a potential request schema if needed later (not strictly required for file upload endpoint)
# class OCRRequest(BaseModel):
#     image_url: str | None = None # Example: if supporting URL input
#     image_content: bytes | None = None # Example: if supporting base64 encoded content