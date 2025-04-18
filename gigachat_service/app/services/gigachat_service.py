import httpx
import uuid
import time
import logging
from cachetools import TTLCache, cached
from fastapi import HTTPException, status

from app.core.config import settings, logger
from app.models.schemas import (
    GigaChatCompletionRequest, GigaChatCompletionResponse,
    TokenResponse, ChatServiceRequest, GigaChatMessageInput
)

# Cache for the access token (TTL slightly less than 30 mins, e.g., 29 mins = 1740 secs)
# Cache key will be static as we only need one token for the service instance
token_cache = TTLCache(maxsize=1, ttl=1740)
CACHE_KEY = "gigachat_access_token"

async def _fetch_new_access_token() -> str:
    """Fetches a new access token from the GigaChat OAuth endpoint."""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {settings.GIGACHAT_AUTH_KEY}'
    }
    data = {'scope': settings.GIGACHAT_SCOPE}
    request_url = settings.GIGACHAT_TOKEN_URL

    logger.info(f"Requesting new GigaChat access token from {request_url} with scope {settings.GIGACHAT_SCOPE}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(request_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            token_data = response.json()
            token_response = TokenResponse(**token_data)
            logger.info(f"Successfully obtained new GigaChat access token, expires at {token_response.expires_at}")
            return token_response.access_token

        except httpx.RequestError as exc:
            logger.error(f"HTTP request error while fetching GigaChat token: {exc}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"Error connecting to GigaChat auth service: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP status error while fetching GigaChat token: {exc.response.status_code} - {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code,
                                detail=f"GigaChat auth service returned error: {exc.response.text}")
        except Exception as exc:
            logger.error(f"Unexpected error fetching GigaChat token: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"An unexpected error occurred while fetching the GigaChat token: {exc}")

@cached(token_cache)
async def get_access_token() -> str:
    """Gets the access token, utilizing the cache."""
    logger.info("Attempting to get GigaChat access token (checking cache first)...")
    # The @cached decorator handles checking the cache and calling _fetch_new_access_token if needed
    token = await _fetch_new_access_token()
    if not token: # Should not happen with current logic, but as a safeguard
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to retrieve access token after cache miss.")
    return token


async def get_chat_completion(request_data: ChatServiceRequest) -> GigaChatCompletionResponse:
    """
    Calls the GigaChat /chat/completions endpoint.

    Args:
        request_data: The request data containing messages and optional parameters.

    Returns:
        The parsed response from the GigaChat API.

    Raises:
        HTTPException: If there's an error during the API call.
    """
    access_token = await get_access_token()
    if not access_token:
        # This case should ideally be handled by get_access_token raising an exception
        logger.error("Failed to obtain access token for chat completion.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not retrieve GigaChat access token.")

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        # Add X-Client-ID, X-Request-ID, X-Session-ID if needed based on documentation/requirements
    }

    # Prepare the payload for GigaChat API
    model_to_use = request_data.model or settings.GIGACHAT_DEFAULT_MODEL
    payload = GigaChatCompletionRequest(
        model=model_to_use,
        messages=request_data.messages,
        temperature=request_data.temperature, # Pass through optional params
        max_tokens=request_data.max_tokens,
        # Add other params like top_p, n, stream, repetition_penalty if needed
    ).model_dump(exclude_none=True) # Use model_dump for Pydantic v2, exclude unset optional fields

    request_url = settings.GIGACHAT_CHAT_URL
    logger.info(f"Sending chat completion request to GigaChat ({model_to_use}) at {request_url}")
    # logger.debug(f"GigaChat request payload: {payload}") # Be careful logging potentially large/sensitive message content

    async with httpx.AsyncClient(timeout=60.0) as client: # Increased timeout for potentially long LLM responses
        try:
            response = await client.post(request_url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            logger.info("Successfully received chat completion response from GigaChat.")
            # logger.debug(f"GigaChat response data: {response_data}")
            return GigaChatCompletionResponse(**response_data)

        except httpx.RequestError as exc:
            logger.error(f"HTTP request error during GigaChat chat completion: {exc}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"Error connecting to GigaChat chat service: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP status error during GigaChat chat completion: {exc.response.status_code} - {exc.response.text}")
            # Attempt to parse error details if available
            error_detail = f"GigaChat chat service returned error: Status {exc.response.status_code}"
            try:
                error_json = exc.response.json()
                error_detail += f" - {error_json}"
            except Exception:
                 error_detail += f" - {exc.response.text}"

            raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
        except Exception as exc:
            logger.error(f"Unexpected error during GigaChat chat completion: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"An unexpected error occurred during GigaChat chat completion: {exc}")