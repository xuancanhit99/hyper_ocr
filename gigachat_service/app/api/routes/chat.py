from fastapi import APIRouter, Depends, HTTPException, status, Body, Header
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, Dict, Any
import logging

from app.core.config import settings # Import settings
from app.services.gigachat_service import GigaChatService
from app.models.schemas import ChatCompletionRequest # Assume this schema exists

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_gigachat_service(
    gigachat_auth_key: Optional[str] = Header(None, alias="x-api-key", description="Optional GigaChat Authorization Key via x-api-key header")
) -> GigaChatService:
    """Dependency to get GigaChatService with optional header auth key."""
    return GigaChatService(auth_key=gigachat_auth_key)


@router.post("/generate-text")


@router.post("/generate-text")
async def create_chat_completion(
    request_body: Dict[str, Any] = Body(...), # Accept flexible request body
    gigachat_service: GigaChatService = Depends(get_gigachat_service) # Use the new dependency
):
    """
    Creates a chat completion using the GigaChat API, mimicking OpenAI structure,
    with support for Grok-like request formats.
    """
    try:
        # Extract fields from the flexible request body
        user_message = request_body.get("message")
        history = request_body.get("history", []) # Default to empty list if history is not provided
        model_name = request_body.get("model_name") # Grok uses model_name
        temperature = request_body.get("temperature", 0.7) # Default temperature
        max_tokens = request_body.get("max_tokens")
        stream = request_body.get("stream", False) # Default to non-streaming

        # Validate required fields (at least message is needed for a new turn)
        if user_message is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body must contain a 'message' field."
            )
            
        # Construct the messages list in OpenAI format expected by GigaChatService
        # Include history first, then the current user message
        messages = []
        # Add history messages
        for historical_message in history:
             if "role" in historical_message and "content" in historical_message:
                  messages.append({"role": historical_message["role"], "content": historical_message["content"]})
             else:
                  # Log a warning if history message format is unexpected
                  logger.warning(f"Skipping malformed history message: {historical_message}")

        # Add the current user message
        messages.append({"role": "user", "content": user_message})


        # Determine the model to use
        # Use model_name from request if provided, otherwise use default from settings
        model_to_use = model_name or settings.GIGACHAT_DEFAULT_MODEL # Use imported settings
        
        if not model_to_use:
             # This should ideally not happen if GIGACHAT_DEFAULT_MODEL is set,
             # but as a safeguard.
             raise HTTPException(
                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="GigaChat model name is not provided and no default model is configured."
             )


        # Prepare parameters for GigaChatService
        service_params = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            "max_tokens": max_tokens # Pass max_tokens if provided
        }
        
        # Remove max_tokens if it's None, as GigaChatService expects int or None
        if service_params["max_tokens"] is None:
            del service_params["max_tokens"]

        if stream:
            # For streaming requests
            generator = gigachat_service.create_chat_completion(
               **service_params
            )
            # FastAPI's StreamingResponse handles the SSE formatting based on the generator
            return StreamingResponse(generator, media_type="text/event-stream")
        else:
            # For non-streaming requests
            response_data = await gigachat_service.create_chat_completion(
                **service_params
            )
            # create_chat_completion already returns data in OpenAI format for non-stream
            return JSONResponse(content=response_data)

    except HTTPException as e:
        logger.error(f"HTTPException in chat completion route: {e.detail} (Status: {e.status_code})")
        # Re-raise HTTPExceptions raised by the service (e.g., auth errors, rate limits)
        raise e
    except Exception as e:
        logger.exception("An unexpected error occurred during chat completion processing.")
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {e}"
        )