import httpx
import json
import uuid
import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO)

class GigaChatService:
    """Service for interacting with the GigaChat API."""

    def __init__(self, auth_key: Optional[str] = None):
        """Initializes the GigaChat service.

        Args:
            auth_key: Optional GigaChat authorization key. If not provided,
                      will fall back to settings.GIGACHAT_AUTH_KEY.
        """
        self.scope = settings.GIGACHAT_SCOPE
        self._default_auth_key = auth_key or settings.GIGACHAT_AUTH_KEY
        self._access_token = None
        self._token_expires_at = 0

    async def _get_access_token(self, auth_key: Optional[str] = None) -> str:
        """Retrieves or renews the access token using the provided auth_key or the default one."""
        # Use provided auth_key if available, otherwise fall back to the default
        key_to_use = auth_key or self._default_auth_key
        
        # Check if the key_to_use is valid
        if not key_to_use or len(key_to_use) < 10:  # Basic check
            raise ValueError("Invalid GigaChat Authorization Key provided.")

        current_time = time.time()
        # Check if token is still valid for at least 5 minutes
        if self._access_token and self._token_expires_at > current_time + 300: 
            logging.info("Using cached GigaChat access token.")
            return self._access_token

        logging.info("Requesting new GigaChat access token.")
        token_url = settings.GIGACHAT_TOKEN_URL  # Use the full token URL from settings
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Bearer {key_to_use}'
        }
        payload = {'scope': self.scope}

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(token_url, headers=headers, data=payload, timeout=30.0)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data['access_token']
                # expires_at is in milliseconds, convert to seconds
                self._token_expires_at = current_time + (token_data['expires_at'] / 1000)
                logging.info("Successfully obtained new GigaChat access token.")
                return self._access_token
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = f"GigaChat token request failed (Status: {status_code})"
            try:
                error_data = e.response.json()
                api_err_msg = error_data.get("message") or error_data.get("error_description")
                if api_err_msg:
                    error_detail = f"GigaChat Token Error: {api_err_msg}"
            except Exception:
                pass
            logging.error(f"GigaChat Token Error: {error_detail} (Status: {status_code})")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_detail) from e
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logging.error(f"Could not connect to GigaChat for token: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not connect to GigaChat authentication service.") from e
        except (KeyError, TypeError) as e:
            logging.error(f"Failed to parse GigaChat token response: {e}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid response from GigaChat authentication service.") from e

    async def _make_request(
        self,
        auth_key: Optional[str] = None,
        payload: Dict[str, Any] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Dict[str, Any]]: # Changed return type hint for clarity
        """Helper function to prepare request details for the GigaChat API."""
        # Use provided auth_key or default
        key_to_use = auth_key or self._default_auth_key
        
        if not key_to_use:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GigaChat Authorization Key was not provided or found.")

        try:
            # Always get a fresh token before making the chat request, or use cached one if valid
            access_token = await self._get_access_token(key_to_use)
        except ValueError as e:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        except HTTPException as e:
            raise e # Re-raise specific HTTP exceptions from token request

        chat_url = settings.GIGACHAT_CHAT_URL  # Use the full chat URL from settings
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json' if not stream else 'text/event-stream',
            'Authorization': f'Bearer {access_token}'
        }

        # Return the request details (URL, headers, payload)
        return {
            "chat_url": chat_url,
            "headers": headers,
            "payload": payload
        }


    async def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        auth_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None, # GigaChat uses max_tokens, not max_length
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
        """
        Generates a chat completion using the GigaChat API, mimicking OpenAI structure.
        Uses provided auth_key or falls back to default.
        """
        # GigaChat payload structure
        payload = {
            "model": model,
            "messages": messages, # GigaChat uses the same message structure as OpenAI
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens # Use max_tokens if provided

        # Get request details (includes obtaining/refreshing token)
        request_info = await self._make_request(auth_key=auth_key, payload=payload, stream=stream)

        if stream:
            # Delegate to stream_chat_completion to handle the actual streaming HTTP request
            # Pass all necessary parameters, including the obtained request_info
            return self.stream_chat_completion(model, request_info)
        else:
            # For non-streaming, make the actual HTTP request here
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    logging.debug(f"GigaChat Request Payload (non-stream): {payload}")
                    response = await client.post(
                        request_info["chat_url"],
                        json=request_info["payload"],
                        headers=request_info["headers"],
                        timeout=90.0 # Increased timeout for generation
                    )
                    response.raise_for_status()
                    giga_response = response.json()
                    logging.debug(f"GigaChat Response Data (non-stream): {giga_response}")

                # Transform GigaChat response to OpenAI/Grok format
                # Assuming GigaChat non-stream response structure is similar to OpenAI's
                # (single choice with a message and finish_reason)
                
                # Check for potential errors within the response body even if status is 2xx
                if "error" in giga_response:
                     error_detail = giga_response.get("error", {}).get("message", "Unknown GigaChat API error in response body.")
                     error_code = giga_response.get("error", {}).get("code", "unknown_error")
                     logging.error(f"GigaChat API returned an error in response body: {error_detail} (Code: {error_code})")
                     raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY, # Treat API-level errors as bad gateway
                        detail=f"GigaChat API Error: {error_detail} (Code: {error_code})"
                     )


                finish_reason = giga_response.get("choices", [{}])[0].get("finish_reason", "stop")
                # GigaChat might return 'stop' or 'length' or 'model_length' etc.
                # Map GigaChat finish reasons to OpenAI's common ones if necessary, or pass through
                # For now, pass through the finish_reason from GigaChat

                response_message = giga_response.get("choices", [{}])[0].get("message", {"role": "assistant", "content": ""})
                
                # Handle potential missing content or message structure
                if not response_message or not isinstance(response_message, dict):
                    logging.error(f"Unexpected message structure in GigaChat non-stream response: {giga_response}")
                    response_message = {"role": "assistant", "content": ""} # Default to empty assistant message

                prompt_tokens = giga_response.get("usage", {}).get("prompt_tokens")
                completion_tokens = giga_response.get("usage", {}).get("completion_tokens")
                total_tokens = giga_response.get("usage", {}).get("total_tokens")

                # Transform GigaChat response to simplified Grok-like format
                
                # Extract response text from the first choice
                response_text = giga_response.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Extract the model name used (already available as a parameter)
                model_used = model

                grok_formatted_response = {
                    "response_text": response_text,
                    "model_used": model_used
                }

                return grok_formatted_response

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_detail = f"GigaChat API request failed (Status: {status_code})"
                try:
                    error_data = e.response.json()
                    api_err_msg = error_data.get("message")
                    if api_err_msg:
                        error_detail = f"GigaChat API Error: {api_err_msg}"
                        if status_code == 401:
                            error_detail = "GigaChat request failed: Authentication error (check token/key)."
                        elif status_code == 429:
                            status_code = status.HTTP_429_TOO_MANY_REQUESTS
                            error_detail = "GigaChat service rate limited. Please try again later."
                        elif status_code == 400:
                            status_code = status.HTTP_400_BAD_REQUEST
                            error_detail = f"GigaChat API rejected input: {api_err_msg}"
                        else:
                             # Catch other 4xx/5xx errors and map to 502 or other appropriate status
                             status_code = status.HTTP_502_BAD_GATEWAY if status_code < 500 else status_code # Propagate 5xx, map 4xx (except 400, 401, 429) to 502
                             error_detail = f"GigaChat API returned error: {api_err_msg}"

                except Exception:
                     # If JSON parsing fails, use generic error message based on status code
                     if status_code == 401: status_code = status.HTTP_401_UNAUTHORIZED; error_detail = "GigaChat request failed: Authentication error."
                     elif status_code == 429: status_code = status.HTTP_429_TOO_MANY_REQUESTS; error_detail = "GigaChat service rate limited."
                     elif status_code == 400: status_code = status.HTTP_400_BAD_REQUEST; error_detail = "GigaChat API rejected input."
                     else: status_code = status.HTTP_502_BAD_GATEWAY if status_code < 500 else status_code; error_detail = f"Bad Gateway connecting to GigaChat API (Status: {e.response.status_code})."

                logging.error(f"GigaChat API Error: {error_detail} (Status: {status_code})")
                raise HTTPException(status_code=status_code, detail=error_detail) from e
            except httpx.TimeoutException as e:
                 logging.error("Request to GigaChat API timed out.")
                 raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request to GigaChat API timed out.") from e
            except httpx.RequestError as e:
                 logging.error(f"Could not connect to GigaChat API: {e}")
                 raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not connect to the backend GigaChat service.") from e
            except (KeyError, IndexError, TypeError) as parse_error:
                 # Note: This catch block is less likely to be hit now for the successful path
                 # because the response is formatted before parsing the full OpenAI-like structure.
                 # However, it's kept for robustness in case of unexpected GigaChat response formats.
                 logging.error(f"Failed to parse GigaChat API response for Grok format: {parse_error}. Response: {giga_response if 'giga_response' in locals() else 'N/A'}")
                 raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to parse expected data from GigaChat API response for Grok format.") from parse_error
            except Exception as e:
                 logging.exception("An unexpected error occurred in GigaChat service request.")
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal error occurred.") from e


    async def stream_chat_completion(
        self,
        model: str,
        request_info: Dict[str, Any] # Pass request_info directly from _make_request
    ) -> AsyncGenerator[str, None]:
        """Generates and streams chat completions from GigaChat using SSE, formatted for OpenAI."""
        
        request_id = f"chatcmpl-giga-{uuid.uuid4().hex}"
        created_time = int(time.time())
        first_chunk = True

        try:
           # Create a new client within this method for streaming
           async with httpx.AsyncClient(verify=False) as client:
               # Use the request_info obtained from _make_request
               async with client.stream(
                   "POST",
                   request_info["chat_url"],
                   json=request_info["payload"],
                   headers=request_info["headers"],
                   timeout=90.0 # Increased timeout for generation
               ) as response:
                   # Check for HTTP errors *before* iterating
                   if response.status_code >= 400:
                       error_body = await response.aread()
                       status_code = response.status_code
                       error_detail = f"GigaChat API stream request failed (Status: {status_code})"
                       try:
                           error_data = json.loads(error_body.decode())
                           api_err_msg = error_data.get("message") or error_data.get("error") # Check both keys
                           if api_err_msg:
                               error_detail = f"GigaChat API Error: {api_err_msg}"
                       except Exception:
                           error_detail += f" - Body: {error_body.decode()[:200]}"

                       # Map specific errors for failover
                       if status_code == 401: status_code = status.HTTP_401_UNAUTHORIZED
                       elif status_code == 429: status_code = status.HTTP_429_TOO_MANY_REQUESTS
                       elif status_code == 400: status_code = status.HTTP_400_BAD_REQUEST

                       logging.error(f"GigaChat Stream Error: {error_detail} (Status: {status_code})")
                       # RAISE HTTPException instead of yielding SSE error
                       raise HTTPException(status_code=status_code, detail=error_detail)
                   else:
                       # If status is OK, proceed with streaming
                       async for line in response.aiter_lines():
                           if not line:
                               continue

                           # Handle keep-alive lines or other non-data lines
                           if not line.startswith("data:"):
                               logging.debug(f"Received non-data line from GigaChat stream: {line.strip()}")
                               continue

                           # Process data line
                           chunk_data_str = line.strip()[len("data: "):]

                           if chunk_data_str == "[DONE]":
                               yield "data: [DONE]\n\n"
                               break

                           try:
                                chunk_data = json.loads(chunk_data_str)

                                # Check for potential errors within the chunk
                                if "error" in chunk_data:
                                    logging.error(f"GigaChat stream chunk contained an error: {chunk_data['error']}")
                                    # Yield an error chunk formatted for OpenAI/Grok
                                    error_message = chunk_data["error"].get("message", "Unknown streaming error")
                                    error_type = chunk_data["error"].get("type", "api_error")
                                    error_code = chunk_data["error"].get("code", None)
                                    
                                    error_payload = {
                                        "id": request_id,
                                        "object": "chat.completion.chunk",
                                        "created": created_time,
                                        "model": model,
                                        "choices": [{
                                            "index": 0,
                                            "delta": {},
                                            "finish_reason": "error", # Indicate stream ended due to error
                                            "error": { # Add error details
                                                 "message": error_message,
                                                 "type": error_type,
                                                 "code": error_code
                                            }
                                        }]
                                    }
                                    yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                                    # Decide if you want to stop streaming or try to continue.
                                    # Stopping is safer in case of persistent errors.
                                    # yield "data: [DONE]\n\n" # Optional: send DONE after error
                                    # return # Optional: stop the generator
                                    continue # Continue processing if possible, but log the error


                                openai_chunk = {
                                    "id": request_id,
                                    "object": "chat.completion.chunk",
                                    "created": created_time,
                                    "model": model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": None # finish_reason comes in the final chunk typically
                                    }]
                                }

                                giga_delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                                giga_content = giga_delta.get("content")
                                giga_role = giga_delta.get("role") # Role should only appear in the first chunk
                                # GigaChat sends finish_reason in the chunk itself
                                finish_reason = chunk_data.get("choices", [{}])[0].get("finish_reason") 

                                # Add role to delta in the first chunk if present
                                if first_chunk and giga_role:
                                    openai_chunk["choices"][0]["delta"]["role"] = giga_role
                                    first_chunk = False # Role should not repeat

                                # Add content if present
                                if giga_content is not None:
                                    openai_chunk["choices"][0]["delta"]["content"] = giga_content
                                    # Note: If the first chunk only contains role, first_chunk remains True until content arrives.
                                    # This is fine, as role only appears in the first chunk where delta is not empty.

                                # Add finish_reason if present in this chunk (should be the last one)
                                if finish_reason:
                                    openai_chunk["choices"][0]["finish_reason"] = finish_reason

                                # Only yield if there's actual content or finish_reason to send
                                if openai_chunk["choices"][0]["delta"] or openai_chunk["choices"][0]["finish_reason"]:
                                     yield f"data: {json.dumps(openai_chunk, ensure_ascii=False)}\n\n"

                           except json.JSONDecodeError:
                               logging.warning(f"Received non-JSON data line from GigaChat stream: {line.strip()}")
                               # Optionally yield an error chunk here too
                               error_payload = {
                                    "id": request_id,
                                    "object": "chat.completion.chunk",
                                    "created": created_time,
                                    "model": model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "error",
                                        "error": {
                                             "message": f"Failed to decode JSON from stream: {line.strip()}",
                                             "type": "json_decode_error"
                                        }
                                    }]
                                }
                               yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                               # yield "data: [DONE]\n\n" # Optional: send DONE after error
                               # return # Optional: stop the generator
                           except Exception as e:
                               logging.error(f"Error processing GigaChat stream chunk: {e} - Line: {line.strip()}")
                               # Yield a more general error chunk
                               error_payload = {
                                    "id": request_id,
                                    "object": "chat.completion.chunk",
                                    "created": created_time,
                                    "model": model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "error",
                                        "error": {
                                             "message": f"Internal error processing stream chunk: {e}",
                                             "type": "processing_error"
                                        }
                                    }]
                                }
                               yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                               # yield "data: [DONE]\n\n" # Optional: send DONE after error
                               # return # Optional: stop the generator

        except httpx.HTTPStatusError as e: 
            # This catch block might be less frequent now that status is checked inside `with client.stream`,
            # but keep it for safety for other potential HTTP errors outside the stream loop.
            status_code = e.response.status_code if hasattr(e, 'response') else 500
            error_detail = f"GigaChat Stream HTTP Status Error: {e}"
            # Map specific errors
            if status_code == 401: status_code = status.HTTP_401_UNAUTHORIZED
            elif status_code == 429: status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif status_code == 400: status_code = status.HTTP_400_BAD_REQUEST

            logging.error(f"GigaChat Stream HTTPStatusError caught outside stream loop: {error_detail} (Status: {status_code})")
            # RAISE HTTPException
            raise HTTPException(status_code=status_code, detail=error_detail) from e
        except HTTPException as e: # Catch exceptions from _make_request (e.g., token error)
            logging.error(f"GigaChat Stream Setup Error (from _make_request): {e.detail} (Status: {e.status_code})")
            # RAISE HTTPException (re-raise)
            raise e
        except httpx.TimeoutException as e:
             logging.error("Stream request to GigaChat API timed out.")
             raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Stream request to GigaChat API timed out.") from e
        except httpx.RequestError as e:
             logging.error(f"Could not connect to GigaChat API for stream: {e}")
             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not connect to the backend GigaChat service for streaming.") from e
        except Exception as e:
            logging.exception(f"Unexpected error during GigaChat streaming for model {model}")
            # RAISE HTTPException
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error during GigaChat streaming: {e}") from e

        # Ensure DONE is sent even if the stream finishes without an explicit [DONE] from GigaChat
        # This might depend on GigaChat's exact SSE format. If GigaChat guarantees [DONE],
        # this final yield is redundant but harmless. If not, it's necessary.
        # Based on the provided logic, the inner loop breaks on [DONE], so this might only
        # be reached on error or unexpected stream end. Yielding DONE here ensures the client
        # receives a termination signal.
        # yield "data: [DONE]\n\n" # Already handled by the break inside the loop if [DONE] is received