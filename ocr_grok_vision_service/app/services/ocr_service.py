# app/services/ocr_service.py
import httpx
import base64
from fastapi import HTTPException, status, UploadFile
from app.core.config import get_settings
from app.models.schemas import ChatMessage # Import ChatMessage schema
import mimetypes

settings = get_settings()

class OCRService:
    def __init__(self):
        self.api_endpoint = f"{settings.XAI_API_BASE_URL}/chat/completions"
        self.api_key = settings.XAI_API_KEY
        self.default_prompt = "Extract all visible text from this image. Returns only the text content."

        if not self.api_key or "YOUR_XAI_API_KEY" in self.api_key:
            raise ValueError("OCR service is not configured: Missing or invalid XAI_API_KEY.")

    async def extract_text_from_image(
        self,
        image_file: UploadFile,
        model_name: str | None = None,
        prompt: str | None = None,
        api_key: str | None = None
    ) -> tuple[str, str]:
        """
        Sends the image to the Grok Vision API and returns extracted text.
        """
        selected_model = model_name or settings.GROK_VISION_DEFAULT_MODEL # Use vision model default
        used_api_key = api_key or self.api_key
        used_prompt = prompt or self.default_prompt

        try:
            image_content = await image_file.read()
            mime_type, _ = mimetypes.guess_type(image_file.filename or "image.bin")
            if mime_type not in settings.ALLOWED_CONTENT_TYPES:
                mime_type = image_file.content_type
                if mime_type not in settings.ALLOWED_CONTENT_TYPES:
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
                            {"type": "text", "text": used_prompt}
                        ]
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.1,
            }
            headers = {
                "Authorization": f"Bearer {used_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_endpoint, json=payload, headers=headers, timeout=90.0)

            try:
                response.raise_for_status()
                response_data = response.json()
                extracted_text = response_data["choices"][0]["message"]["content"].strip()

                refusal_phrases = ["unable to process", "cannot fulfill this request", "cannot extract text", "i cannot process images"]
                if any(phrase in extracted_text.lower() for phrase in refusal_phrases):
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
                    if status_code == 401:
                        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                        error_detail = "OCR service failed: Invalid API Key configured."
                    elif status_code == 429:
                        status_code = status.HTTP_429_TOO_MANY_REQUESTS
                        error_detail = "OCR service rate limited by Grok API."
                    elif status_code == 400:
                        status_code = status.HTTP_400_BAD_REQUEST
                        error_detail = "Grok API rejected input."
                    else:
                        status_code = status.HTTP_502_BAD_GATEWAY

                raise HTTPException(status_code=status_code, detail=error_detail) from e

            except (KeyError, IndexError, TypeError) as parse_error:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to parse expected data from Grok API response."
                ) from parse_error

        except httpx.TimeoutException as e:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to Grok API timed out."
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to the backend OCR service (Grok API)."
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OCR Service is not properly configured: {e}"
            ) from e
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected internal error occurred during OCR processing."
            ) from e
    async def generate_text_response(
        self,
        message: str,
        history: list[ChatMessage],
        model_name: str | None = None,
        api_key: str | None = None
    ) -> tuple[str, str]:
        """
        Sends the chat history and new message to the Grok API and returns the text response.
        """
        selected_model = model_name or settings.GROK_TEXT_DEFAULT_MODEL # Use text model default
        used_api_key = api_key or self.api_key

        # Format messages for Grok API (list of role/content dicts)
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in history]
        # Add the new user message
        formatted_messages.append({"role": "user", "content": message})

        payload = {
            "model": selected_model,
            "messages": formatted_messages,
            "max_tokens": 3000, # Consider making this configurable
            "temperature": 0.3, # Adjust temperature for chat if needed
        }
        headers = {
            "Authorization": f"Bearer {used_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_endpoint, json=payload, headers=headers, timeout=90.0)

            # Reuse the error handling logic, slightly adapted for chat context
            try:
                response.raise_for_status()
                response_data = response.json()
                # Ensure the path to the response text is correct for chat completions
                response_text = response_data["choices"][0]["message"]["content"].strip()

                # Optional: Check for refusal phrases if needed for chat
                # refusal_phrases = [...]
                # if any(phrase in response_text.lower() for phrase in refusal_phrases):
                #     response_text = "Model indicated it could not fulfill the chat request."

                return response_text, selected_model

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_detail = f"Grok API chat request failed (Status: {status_code})"
                try:
                    error_data = e.response.json()
                    api_err_msg = error_data.get("error", {}).get("message") or error_data.get("detail")
                    if api_err_msg:
                        error_detail = f"Grok API Error: {api_err_msg}"
                        if "authentication" in api_err_msg.lower() or status_code == 401:
                            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                            error_detail = "Chat service failed: Invalid API Key configured."
                        elif "rate limit" in api_err_msg.lower() or status_code == 429:
                            status_code = status.HTTP_429_TOO_MANY_REQUESTS
                            error_detail = "Chat service rate limited by Grok API. Please try again later."
                        elif "invalid input" in api_err_msg.lower() or status_code == 400:
                             status_code = status.HTTP_400_BAD_REQUEST
                             error_detail = f"Grok API rejected input: {api_err_msg}"
                        else:
                             status_code = status.HTTP_502_BAD_GATEWAY # Default to bad gateway for other API errors
                except Exception: # Failed to parse error JSON
                     if status_code == 401:
                         status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                         error_detail = "Chat service failed: Invalid API Key configured."
                     elif status_code == 429:
                         status_code = status.HTTP_429_TOO_MANY_REQUESTS
                         error_detail = "Chat service rate limited by Grok API."
                     elif status_code == 400:
                         status_code = status.HTTP_400_BAD_REQUEST
                         error_detail = "Grok API rejected input."
                     else:
                         status_code = status.HTTP_502_BAD_GATEWAY

                raise HTTPException(status_code=status_code, detail=error_detail) from e

            except (KeyError, IndexError, TypeError) as parse_error:
                # Log parse_error details
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to parse expected data from Grok API chat response."
                ) from parse_error

        except httpx.TimeoutException as e:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to Grok API for chat timed out."
            ) from e
        except httpx.RequestError as e:
            # Log e details
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to the backend chat service (Grok API)."
            ) from e
        except ValueError as e: # Catch potential init errors if called directly without Depends
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                 detail=f"Chat Service is not properly configured: {e}"
             ) from e
        except HTTPException as e: # Re-raise specific HTTP exceptions
            raise e
        except Exception as e:
            # Log unexpected error e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected internal error occurred during chat processing."
            ) from e
