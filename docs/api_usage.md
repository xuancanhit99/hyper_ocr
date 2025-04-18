# 📄 API Documentation - OCR and Chat Services (Gemini, Grok, GigaChat, Cloud Vision)

This document describes how to integrate and use the APIs provided by the OCR Gemini, OCR Grok Vision, GigaChat, and OCR Cloud Vision services.

## ℹ️ General Information

### Base URLs (Default when running via Docker Compose)

*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`
*   **GigaChat Service:** `http://localhost:8005` (Default, check `gigachat_service/.env`)
*   **OCR Cloud Vision Service:** `http://localhost:8002`

*(Note: These ports may change depending on your deployment configuration)*

### 🔑 Authentication

*   **Gemini & Grok Services:** These services can use API Key-based authentication via the `X-API-Key` HTTP Header (Google API Key for Gemini, XAI API Key for Grok). If the API key is configured in the service's `.env` file on the server-side, you do not need to send this header. Use this header only if you want to override or provide the API key per request.
*   **GigaChat Service:** This service handles authentication internally using OAuth 2.0 with the `GIGACHAT_AUTH_KEY` and `GIGACHAT_SCOPE` configured in its `.env` file. It automatically fetches and refreshes access tokens. No specific authentication headers are required when calling this service's endpoints.
*   **Cloud Vision Service:** This service authenticates using Google Cloud Application Default Credentials (ADC). Typically, this involves setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable within the service's environment (e.g., via the `.env` file and Docker Compose) to point to a service account key file. No specific HTTP header is usually required for authentication when using ADC.

---

## ♊ 1. OCR Gemini Service

**Base URL:** `http://localhost:8000`

### 📸 1.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Gemini Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) Google API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file to process (Allowed types: `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`).
*   **Query Parameters:**
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

### 💬 1.2. Text Chat

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

## 🤖 2. OCR Grok Vision Service

**Base URL:** `http://localhost:8001`

### 📸 2.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Grok Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) XAI API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file to process (Allowed types: `image/jpeg`, `image/png`).
*   **Query Parameters:**
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

### 💬 2.2. Text Chat

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

## 💬 3. GigaChat Service

**Base URL:** `http://localhost:8005` (Default)

### 💬 3.1. Text Chat

*   **Endpoint:** `POST /chat`
*   **Description:** Send a message and chat history to get a response from the GigaChat model. Authentication is handled internally by the service.
*   **Headers:**
   *   `Content-Type`: `application/json`
*   **Request Body:** `application/json`
   ```json
   {
     "messages": [
       {"role": "user", "content": "Привет! Как дела?"},
       {"role": "assistant", "content": "Привет! У меня все отлично, спасибо."},
       {"role": "user", "content": "Расскажи анекдот."}
     ],
     "model": "GigaChat-Pro", // Optional: override default model (e.g., GigaChat, GigaChat-Max)
     "temperature": 0.7, // Optional: override temperature
     "max_tokens": 100 // Optional: override max tokens
   }
   ```
   *   `messages`: (Required) List of previous messages. `role` must be `"user"`, `"assistant"`, or `"system"`.
   *   `model`: (Optional) Specific GigaChat model name to use (e.g., `GigaChat`, `GigaChat-Pro`, `GigaChat-Max`). Defaults to the value from configuration (`GIGACHAT_DEFAULT_MODEL`).
   *   `temperature`: (Optional) Sampling temperature (float between 0 and 2).
   *   `max_tokens`: (Optional) Maximum number of tokens to generate.
*   **Response (Success - 200 OK):** `application/json`
   ```json
   {
     "response": {
       "role": "assistant",
       "content": "Response from the GigaChat model..."
       // "function_call": null // If function calling is used
     },
     "model_used": "GigaChat-Pro", // Example model used
     "usage": {
       "prompt_tokens": 50,
       "completion_tokens": 75,
       "total_tokens": 125
     }
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
   curl -X POST "http://localhost:8005/chat" \
        -H "Content-Type: application/json" \
        -d '{
              "messages": [
                {"role": "user", "content": "Напиши короткий рассказ о роботе, который научился мечтать."}
              ],
              "model": "GigaChat-Max"
            }'
   ```

---

## ☁️ 4. OCR Cloud Vision Service

**Base URL:** `http://localhost:8002`

### 📸 4.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Google Cloud Vision API.
*   **Authentication:** Uses Google Cloud Application Default Credentials (ADC) configured on the server-side (via `GOOGLE_APPLICATION_CREDENTIALS` environment variable). No specific `X-API-Key` header is needed.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file to process (Supports various formats like JPEG, PNG, GIF, BMP, WEBP, RAW, ICO, PDF, TIFF - check Google Cloud Vision documentation for the full list and limits).
*   **Query Parameters:** None.
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "text": "Full extracted text content...",
      "details": [
        {
          "text": "Word1",
          "bounding_box": [
            {"x": 10, "y": 10},
            {"x": 50, "y": 10},
            {"x": 50, "y": 30},
            {"x": 10, "y": 30}
          ]
        },
        {
          "text": "Word2",
          "bounding_box": [
            {"x": 60, "y": 10},
            {"x": 100, "y": 10},
            {"x": 100, "y": 30},
            {"x": 60, "y": 30}
          ]
        }
        // ... other detected text blocks
      ]
    }
    ```
*   **Response (Error):** `application/json` (Examples: 400, 403, 429, 500, 502)
    ```json
    {
      "detail": "Detailed error description (e.g., 'Permission denied: Check credentials/API key permissions...', 'API quota exceeded...', 'Invalid image format or content...', 'Upstream Google API Error:...')"
    }
    ```
*   **Example (curl):**
    ```bash
    curl -X POST "http://localhost:8002/ocr/extract-text" \
         -F "file=@/path/to/your/image.png"
    ```

---

## ✅ 5. Health Check

All services provide an endpoint to check their operational status.

*   **Endpoint:** `GET /health` (Note: No trailing slash for Cloud Vision)
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
    *   *GigaChat:*
        ```json
        {
          "status": "ok",
          "service": "GigaChat Service"
        }
        ```
    *   *Cloud Vision:*
        ```json
        {
          "status": "ok"
        }
        ```
*   **Example (curl):**
    ```bash
    curl -X GET http://localhost:8000/health
    curl -X GET http://localhost:8001/health
    curl -X GET http://localhost:8005/health # GigaChat health check
    curl -X GET http://localhost:8002/health