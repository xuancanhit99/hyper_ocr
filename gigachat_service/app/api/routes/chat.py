from fastapi import APIRouter, HTTPException, status, Body
from typing import Annotated

from app.models.schemas import ChatServiceRequest, ChatServiceResponse, GigaChatMessageOutput, GigaChatUsage
from app.services.gigachat_service import get_chat_completion
from app.core.config import logger

router = APIRouter()

@router.post(
    "/chat",
    response_model=ChatServiceResponse,
    summary="Process chat messages with GigaChat",
    description="Receives a list of messages and returns the GigaChat model's response.",
    tags=["Chat"]
)
async def process_chat(
    request_data: Annotated[ChatServiceRequest, Body(
        examples=[
            {
                "messages": [
                    {"role": "user", "content": "Привет! Как дела?"}
                ],
                "model": "GigaChat-Pro",
                "temperature": 0.7
            }
        ],
    )]
):
    """
    Endpoint to interact with the GigaChat model.

    - Takes a list of messages representing the conversation history.
    - Optionally allows overriding the default model and other parameters.
    - Calls the GigaChat API via the service layer.
    - Returns the assistant's response along with model and usage info.
    """
    logger.info(f"Received chat request with {len(request_data.messages)} messages.")
    # logger.debug(f"Chat request data: {request_data.model_dump_json(indent=2)}") # Sensitive

    try:
        # Call the service function to get the completion
        giga_response = await get_chat_completion(request_data)

        # Process the response
        if not giga_response.choices:
            logger.error("GigaChat response contained no choices.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="GigaChat returned no response choices.")

        # Assuming we only care about the first choice (n=1 is default)
        first_choice = giga_response.choices[0]
        assistant_message = first_choice.message
        model_used = giga_response.model
        usage_stats = giga_response.usage

        logger.info(f"Successfully processed chat request using model {model_used}.")

        # Format the response according to ChatServiceResponse schema
        service_response = ChatServiceResponse(
            response=assistant_message,
            model_used=model_used,
            usage=usage_stats
        )
        # logger.debug(f"Sending chat response: {service_response.model_dump_json(indent=2)}") # Sensitive

        return service_response

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions raised by the service layer
        logger.warning(f"HTTPException during chat processing: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.exception("An unexpected error occurred during chat processing.") # Log full traceback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An internal server error occurred: {e}")