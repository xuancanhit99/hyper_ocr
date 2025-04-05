# app/services/ocr_service.py
import httpx
import base64
from fastapi import HTTPException, status, UploadFile
from app.core.config import get_settings
import mimetypes

settings = get_settings()

DEFAULT_OCR_PROMPT = "Perform Optical Character Recognition (OCR) on the following image. Extract all visible text as accurately as possible. Preserve the original line breaks and structure of the text found in the image. Output *only* the extracted text, without any additional comments, introductory phrases (like 'Here is the extracted text:'), or explanations."

class OCRService:
    def __init__(self):
        self.api_endpoint = f"{settings.XAI_API_BASE_URL}/chat/completions"
        self.api_key = settings.XAI_API_KEY
        self.ocr_prompt = getattr(settings, 'GROK_OCR_PROMPT', DEFAULT_OCR_PROMPT)

        if not self.api_key or "YOUR_XAI_API_KEY" in self.api_key:
            # Raise immediately during init if misconfigured
            raise ValueError("OCR service is not configured: Missing or invalid XAI_API_KEY.")

    async def extract_text_from_image(self, image_file: UploadFile, model_name: str | None = None) -> tuple[str, str]:
        """
        Sends the image to the official Grok Vision API and returns extracted text.
        """
        selected_model = model_name or settings.GROK_DEFAULT_MODEL
        # Basic check for vision model compatibility (optional)
        # if "vision" not in selected_model.lower() and "grok-2" not in selected_model.lower():
        #     pass # Removed warning

        try:
            image_content = await image_file.read()
            mime_type, _ = mimetypes.guess_type(image_file.filename or "image.bin")
            if mime_type not in ["image/jpeg", "image/png"]:
                 mime_type = image_file.content_type
                 if mime_type not in ["image/jpeg", "image/png"]:
                     raise HTTPException(
                         status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                         detail=f"Unsupported image type '{mime_type}'. Only JPEG and PNG are supported."
                     )

            image_base64 = base64.b64encode(image_content).decode('utf-8')
            data_url = f"data:{mime_type};base64,{image_base64}"

            payload = {
                "model": selected_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url, "detail": "high"}
                            },
                            {"type": "text", "text": self.ocr_prompt}
                        ]
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.1,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient() as client:
                # Removed logger.info
                response = await client.post(self.api_endpoint, json=payload, headers=headers, timeout=90.0)

            try:
                response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx
                response_data = response.json()
                # Removed logger.info

                extracted_text = response_data["choices"][0]["message"]["content"]
                extracted_text = extracted_text.strip()

                refusal_phrases = ["unable to process", "cannot fulfill this request", "cannot extract text", "i cannot process images"]
                if any(phrase in extracted_text.lower() for phrase in refusal_phrases):
                    # Removed logger.warning
                    extracted_text = "Model indicated it could not perform the OCR task on this image."

                return extracted_text, selected_model

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_detail = f"Grok API request failed (Status: {status_code})"
                try:
                    error_data = e.response.json()
                    api_err_msg = error_data.get("error", {}).get("message") or error_data.get("detail")
                    if api_err_msg:
                        error_detail = f"Grok API Error: {api_err_msg}"
                        if "authentication" in api_err_msg.lower() or status_code == 401:
                            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                            error_detail = "OCR service failed: Invalid API Key configured."
                        elif "rate limit" in api_err_msg.lower() or status_code == 429:
                             status_code = status.HTTP_429_TOO_MANY_REQUESTS
                             error_detail = "OCR service rate limited by Grok API. Please try again later."
                        elif "invalid input" in api_err_msg.lower() or status_code == 400:
                            status_code = status.HTTP_400_BAD_REQUEST
                            error_detail = f"Grok API rejected input: {api_err_msg}"
                        else:
                             status_code = status.HTTP_502_BAD_GATEWAY
                except Exception:
                    # Removed logger.warning
                    if status_code == 401:
                        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                        error_detail = "OCR service failed: Invalid API Key configured (unable to parse details)."
                    elif status_code == 429:
                         status_code = status.HTTP_429_TOO_MANY_REQUESTS
                         error_detail = "OCR service rate limited by Grok API (unable to parse details)."
                    elif status_code == 400:
                         status_code = status.HTTP_400_BAD_REQUEST
                         error_detail = "Grok API rejected input (unable to parse details)."
                    else:
                        status_code = status.HTTP_502_BAD_GATEWAY

                # Removed logger.error
                raise HTTPException(status_code=status_code, detail=error_detail) from e

            except (KeyError, IndexError, TypeError) as parse_error:
                # Removed logger.error
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to parse expected data from Grok API response."
                ) from parse_error

        except httpx.TimeoutException as e:
            # Removed logger.error
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to Grok API timed out."
            ) from e
        except httpx.RequestError as e:
            # Removed logger.error
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to the backend OCR service (Grok API)."
            ) from e
        except ValueError as e: # Catch init error
             # Removed logger.critical
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                 detail=f"OCR Service is not properly configured: {e}"
             ) from e
        except HTTPException as e:
             raise e
        except Exception as e:
            # Removed logger.exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected internal error occurred during OCR processing."
            ) from e