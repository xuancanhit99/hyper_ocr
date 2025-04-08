# API Documentation - OCR and Chat Services (Gemini & Grok)

This document describes how to integrate and use the APIs provided by the OCR Gemini and OCR Grok Vision services.

## General Information

### Base URLs (Default when running via Docker Compose)

*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`

*(Note: These ports may change depending on your deployment configuration)*

### Authentication

Both services use API Key-based authentication via HTTP Header.

*   **Header Name:** `X-API-Key`
*   **Value:** The corresponding API key (Google API Key for Gemini, XAI API Key for Grok).

If the API key is configured in the service's `.env` file on the server-side, you do not need to send this header. Use this header if you want to override or provide the API key per request.

---

## 1. OCR Gemini Service

**Base URL:** `http://localhost:8000`

### 1.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Gemini Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) Google API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file to process (Allowed types: `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`).
    *   `prompt`: (Optional) Text string to guide the model (e.g., "Extract only the address"). Defaults to extracting all text.
    *   `model_name`: (Optional) Specific Gemini Vision model name to use (e.g., `gemini-2.0-flash-exp-image-generation`). Defaults to the value from configuration (`GEMINI_VISION_MODEL_NAME`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "image_filename.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Extracted text content...",
      "model_used": "gemini-2.0-flash-exp-image-generation" // Example model used
    }
    ```
*   **Response (Error):** `application/json` (Examples: 400, 422, 500, 503)
    ```json
    {
      "detail": "Detailed error description..."
    }
    ```
*   **Example (curl):**
    ```bash
    curl -X POST "http://localhost:8000/ocr/extract-text?prompt=Extract%20only%20the%20invoice%20number&model_name=gemini-2.0-flash-exp-image-generation" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -F "file=@/path/to/your/image.png"
    ```

### 1.2. Text Chat

*   **Endpoint:** `POST /chat/`
*   **Description:** Send a message and chat history to get a response from the Gemini Text model.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Optional) Google API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "User's new message",
      "history": [
        {"role": "user", "content": "Previous user message"},
        {"role": "assistant", "content": "Previous model response"}
        // ... other turns
      ],
      "model_name": "gemini-2.0-flash" // Optional: override default model (e.g., use flash for chat)
    }
    ```
    *   `message`: (Required) The latest message from the user.
    *   `history`: (Optional) List of previous messages. `role` must be `"user"` or `"assistant"`.
    *   `model_name`: (Optional) Specific Gemini Text model name to use (e.g., `gemini-2.0-flash`). Defaults to the value from configuration (`GEMINI_TEXT_MODEL_NAME`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Response from the Gemini model...",
      "model_used": "gemini-2.0-flash" // Example model used
    }
    ```
*   **Response (Error):** `application/json` (Examples: 400, 500, 503)
    ```json
    {
      "detail": "Detailed error description..."
    }
    ```
*   **Example (curl):**
    ```bash
    curl -X POST "http://localhost:8000/chat/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -d '{
               "message": "What is the capital of France?",
               "history": [
                 {"role": "user", "content": "Hello"},
                 {"role": "assistant", "content": "Hi there!"}
               ],
               "model_name": "gemini-2.0-flash"
             }'
    ```

---

## 2. OCR Grok Vision Service

**Base URL:** `http://localhost:8001`

### 2.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Grok Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) XAI API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file to process (Allowed types: `image/jpeg`, `image/png`).
    *   `prompt`: (Optional) Text string to guide the model. Defaults to extracting all text.
    *   `model_name`: (Optional) Specific Grok Vision model name to use (e.g., `grok-2-vision-1212`). Defaults to the value from configuration (`GROK_VISION_DEFAULT_MODEL`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "image_filename.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Extracted text content...",
      "model_used": "grok-2-vision-1212" // Example model used
    }
    ```
*   **Response (Error):** `application/json` (Examples: 400, 415, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Detailed error description..."
    }
    ```
*   **Example (curl):**
    ```bash
    curl -X POST "http://localhost:8001/ocr/extract-text?model_name=grok-2-vision-1212" \
         -H "X-API-Key: YOUR_XAI_API_KEY" \
         -F "file=@/path/to/your/image.jpg"
    ```

### 2.2. Text Chat

*   **Endpoint:** `POST /chat/`
*   **Description:** Send a message and chat history to get a response from the Grok Text model.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Optional) XAI API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "User's new message",
      "history": [
        {"role": "user", "content": "Previous user message"},
        {"role": "assistant", "content": "Previous model response"}
        // ... other turns
      ],
      "model_name": "grok-2-1212" // Optional: override default model (e.g., use grok-2 for chat)
    }
    ```
    *   `message`: (Required) The latest message from the user.
    *   `history`: (Optional) List of previous messages. `role` must be `"user"` or `"assistant"`.
    *   `model_name`: (Optional) Specific Grok Text model name to use (e.g., `grok-2-1212`). Defaults to the value from configuration (`GROK_TEXT_DEFAULT_MODEL`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Response from the Grok model...",
      "model_used": "grok-2-1212" // Example model used
    }
    ```
*   **Response (Error):** `application/json` (Examples: 400, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Detailed error description..."
    }
    ```
*   **Example (curl):**
    ```bash
    curl -X POST "http://localhost:8001/chat/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_XAI_API_KEY" \
         -d '{
               "message": "Explain the concept of zero-shot learning.",
               "history": [],
               "model_name": "grok-2-1212"
             }'
    ```

---

## 3. Health Check

Both services provide an endpoint to check their operational status.

*   **Endpoint:** `GET /health/`
*   **Description:** Returns the current status of the service.
*   **Response (Success - 200 OK):** `application/json`
    *   *Gemini:*
        ```json
        {
          "status": "ok"
        }
        ```
    *   *Grok:*
        ```json
        {
          "status": "ok",
          "app_name": "OCR Grok Vision Service",
          "app_version": "1.0.0"
        }
        ```
*   **Example (curl):**
    ```bash
    curl -X GET http://localhost:8000/health/
    curl -X GET http://localhost:8001/health/