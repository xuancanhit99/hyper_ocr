from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- GigaChat API Specific Schemas ---

class GigaChatMessageInput(BaseModel):
    """Schema for a single message sent to GigaChat API."""
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant', 'system').")
    content: str = Field(..., description="The content of the message.")
    # attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Optional list of file attachments.") # Add if needed later

class GigaChatCompletionRequest(BaseModel):
    """Schema for the request body sent to GigaChat /chat/completions endpoint."""
    model: str = Field(..., description="The model name to use (e.g., 'GigaChat-Pro').")
    messages: List[GigaChatMessageInput] = Field(..., description="A list of messages comprising the conversation history.")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Sampling temperature.")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Nucleus sampling parameter.")
    n: Optional[int] = Field(1, description="Number of chat completion choices to generate.") # Default seems to be 1 based on docs
    stream: Optional[bool] = Field(False, description="Whether to stream back partial progress.")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate.")
    repetition_penalty: Optional[float] = Field(None, description="Penalty for repeating words.")
    update_interval: Optional[float] = Field(0, description="Update interval for streaming.")
    # function_call: Optional[Any] = None # Add if function calling is needed
    # functions: Optional[List[Any]] = None # Add if function calling is needed

class GigaChatMessageOutput(BaseModel):
    """Schema for a single message received from GigaChat API."""
    role: str
    content: str
    # function_call: Optional[Any] = None # Add if function calling is needed

class GigaChatChoice(BaseModel):
    """Schema for a single choice in the GigaChat response."""
    message: GigaChatMessageOutput
    index: int
    finish_reason: Optional[str] = None # e.g., "stop", "length", "function_call"

class GigaChatUsage(BaseModel):
    """Schema for token usage statistics from GigaChat API."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class GigaChatCompletionResponse(BaseModel):
    """Schema for the full response from GigaChat /chat/completions endpoint."""
    choices: List[GigaChatChoice]
    created: int # Unix timestamp
    model: str
    usage: GigaChatUsage
    object: Optional[str] = None # Seems to be present in some examples

# --- Service Specific Schemas ---

class ChatServiceRequest(BaseModel):
    """Schema for the request body received by our /chat endpoint."""
    messages: List[GigaChatMessageInput] = Field(..., description="Conversation history.")
    model: Optional[str] = Field(None, description="Optional model override.")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Optional temperature override.")
    max_tokens: Optional[int] = Field(None, description="Optional max_tokens override.")
    # Add other parameters if you want the user to be able to override them

class ChatServiceResponse(BaseModel):
    """Schema for the response body sent by our /chat endpoint."""
    response: GigaChatMessageOutput = Field(..., description="The assistant's response message.")
    model_used: str = Field(..., description="The GigaChat model that generated the response.")
    usage: GigaChatUsage = Field(..., description="Token usage statistics.")

class TokenResponse(BaseModel):
    """Schema for the response from GigaChat /oauth endpoint."""
    access_token: str
    expires_at: int # Unix timestamp