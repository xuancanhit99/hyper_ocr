# 📄 API Documentation - Hyper OCR Microservices Suite

This document describes how to integrate and use the APIs provided by the various microservices within the Hyper OCR suite, including OCR, Chat, Authentication, and Utility services.

## ℹ️ General Information

### 🌐 Accessing Services

While services expose individual ports during local development, the **recommended and standard way to interact with the APIs is through the Kong API Gateway**.

*   **API Gateway Base URL:** `http://localhost:7000`

Kong handles routing requests to the appropriate backend service based on the path or other rules you configure. You will need to configure Kong (via Konga UI at `http://localhost:7337` or the Admin API at `http://localhost:7001`) to expose the desired service endpoints through the gateway.

### Direct Service Base URLs (Default - For Development/Debugging Only)

*   **Auth Service:** `http://localhost:8800`
*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`
*   **OCR Cloud Vision Service:** `http://localhost:8002`
*   **OCR Pytesseract Service:** `http://localhost:8003`
*   **Split Bill Service:** `http://localhost:8004`
*   **GigaChat Service:** `http://localhost:8005` (Default, check `gigachat_service/.env`)

*(Note: Direct access might be disabled or ports may change depending on deployment configuration. Always prefer the API Gateway.)*

### 🔑 Authentication

Authentication methods vary per service and how they are exposed via Kong:

*   **Auth Service:** Likely uses JWT Bearer tokens. Obtain a token via a login endpoint (e.g., `/auth/token`) and send it in the `Authorization: Bearer <token>` header for protected endpoints.
*   **Gemini & Grok Services:** Can use API Key-based authentication via the `X-API-Key` HTTP Header (Google API Key for Gemini, XAI API Key for Grok) *if not configured server-side*. If the key is in the service's `.env`, no header is needed for direct access. Kong can be configured to manage or inject these keys.
*   **GigaChat Service:** Handles authentication internally using OAuth 2.0 configured via its `.env` file. No specific authentication headers are typically required when calling its endpoints directly or via Kong (unless Kong adds its own layer).
*   **Cloud Vision Service:** Authenticates using Google Cloud Application Default Credentials (ADC) configured server-side (e.g., `GOOGLE_APPLICATION_CREDENTIALS` environment variable). No specific HTTP header is usually required.
*   **Pytesseract Service:** Likely requires no specific authentication.
*   **Split Bill Service:** Likely requires no specific authentication, but might be protected via the Auth service through Kong.
*   **Kong Gateway:** Kong itself can add authentication layers (e.g., API Keys, JWT, OAuth2) to any route, regardless of the backend service's own authentication. Check Kong's configuration.

---

## 🔐 1. Auth Service

**Base URL (Direct):** `http://localhost:8800`
**(Access via Kong: `http://localhost:7000/auth` - *Example path, configure in Kong*)**

*(Note: Endpoints below are examples and need verification based on actual implementation)*

### 🔑 1.1. Obtain Access Token

*   **Endpoint:** `POST /auth/token`
*   **Description:** Authenticate user credentials to receive a JWT access token.
*   **Request Body:** `application/x-www-form-urlencoded`
    *   `username`: User's email or username.
    *   `password`: User's password.
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "access_token": "your_jwt_token_here",
      "token_type": "bearer"
    }
    ```
*   **Response (Error):** 401 Unauthorized, 422 Unprocessable Entity.

### 👤 1.2. Get Current User

*   **Endpoint:** `GET /users/me`
*   **Description:** Retrieve details for the currently authenticated user.
*   **Headers:**
    *   `Authorization`: `Bearer <your_jwt_token_here>`
*   **Response (Success - 200 OK):** `application/json` (User details schema)
*   **Response (Error):** 401 Unauthorized.

### ➕ 1.3. Register New User

*   **Endpoint:** `POST /users/`
*   **Description:** Create a new user account.
*   **Request Body:** `application/json` (User creation schema, e.g., email, password)
*   **Response (Success - 201 Created):** `application/json` (Created user details)
*   **Response (Error):** 400 Bad Request, 422 Unprocessable Entity.

---

## ♊ 2. OCR Gemini Service

**Base URL (Direct):** `http://localhost:8000`
**(Access via Kong: `http://localhost:7000/ocr/gemini` - *Example path, configure in Kong*)**

### 📸 2.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Gemini Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) Google API Key (if not set server-side).
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file (JPEG, PNG, WEBP, HEIC, HEIF).
*   **Query Parameters:**
    *   `prompt`: (Optional) Guide the model (e.g., "Extract only the address").
    *   `model_name`: (Optional) Override default Gemini Vision model.
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "image.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Extracted text...",
      "model_used": "gemini-pro-vision"
    }
    ```
*   **Example (curl via Kong):**
    ```bash
    # Assuming Kong route /ocr/gemini maps to this service
    curl -X POST "http://localhost:7000/ocr/gemini/ocr/extract-text?prompt=Address" \
         -H "Authorization: Bearer <KONG_JWT_IF_NEEDED>" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \ # If required by Kong or service
         -F "file=@/path/to/image.png"
    ```

### 💬 2.2. Text Chat

*   **Endpoint:** `POST /chat/`
*   **Description:** Send a message and history for a Gemini Text model response.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Optional) Google API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "User's message",
      "history": [ /* {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."} */ ],
      "model_name": "gemini-pro" // Optional override
    }
    ```
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Model response...",
      "model_used": "gemini-pro"
    }
    ```

---

## 🤖 3. OCR Grok Vision Service

**Base URL (Direct):** `http://localhost:8001`
**(Access via Kong: `http://localhost:7000/ocr/grok` - *Example path, configure in Kong*)**

### 📸 3.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file to extract text using the Grok Vision model.
*   **Headers:**
    *   `X-API-Key`: (Optional) XAI API Key (if not set server-side).
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) The image file (JPEG, PNG).
*   **Query Parameters:**
    *   `prompt`: (Optional) Guide the model.
    *   `model_name`: (Optional) Override default Grok Vision model.
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "image.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Extracted text...",
      "model_used": "grok-1.5-vision-preview"
    }
    ```

### 💬 3.2. Text Chat

*   **Endpoint:** `POST /chat/`
*   **Description:** Send a message and history for a Grok Text model response.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Optional) XAI API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "User's message",
      "history": [ /* ... */ ],
      "model_name": "grok-1.5-flash" // Optional override
    }
    ```
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Model response...",
      "model_used": "grok-1.5-flash"
    }
    ```

---

## ☁️ 4. OCR Cloud Vision Service

**Base URL (Direct):** `http://localhost:8002`
**(Access via Kong: `http://localhost:7000/ocr/cloud-vision` - *Example path, configure in Kong*)**

### 📸 4.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Description:** Upload an image file for OCR using Google Cloud Vision API.
*   **Authentication:** Uses server-side ADC. No specific headers needed usually.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) Image file (JPEG, PNG, GIF, BMP, WEBP, RAW, ICO, PDF, TIFF).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "text": "Full extracted text...",
      "details": [
        {
          "text": "Word1",
          "bounding_box": [ /* {"x": ..., "y": ...} */ ]
        }
        // ... other detected blocks
      ]
    }
    ```

---

## 📄 5. OCR Pytesseract Service

**Base URL (Direct):** `http://localhost:8003`
**(Access via Kong: `http://localhost:7000/ocr/tesseract` - *Example path, configure in Kong*)**

### 📸 5.1. Extract Text from Image (OCR)

*   **Endpoint:** `POST /ocr/extract-text` *(Assumption - Verify actual endpoint)*
*   **Description:** Upload an image file for OCR using the Tesseract engine.
*   **Authentication:** Likely none required directly.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Required) Image file (Common formats like PNG, JPEG, TIFF).
*   **Query Parameters:**
    *   `lang`: (Optional) Language code(s) for Tesseract (e.g., `eng`, `rus`, `eng+rus`). Defaults might be configured server-side.
*   **Response (Success - 200 OK):** `application/json` *(Assumption - Verify actual response format)*
    ```json
    {
      "extracted_text": "Text extracted by Tesseract...",
      "language_used": "eng" // Example
    }
    ```
*   **Response (Error):** 400, 422, 500.

---

## 💸 6. Split Bill Service

**Base URL (Direct):** `http://localhost:8004`
**(Access via Kong: `http://localhost:7000/split-bill` - *Example path, configure in Kong*)**

### 🧾 6.1. Split Bill from Image or Text

*   **Endpoint:** `POST /split-bill/` *(Assumption - Verify actual endpoint)*
*   **Description:** Analyzes an image (likely a receipt) or provided text to identify items and potentially split costs.
*   **Authentication:** May require authentication (e.g., JWT via Auth Service) depending on configuration via Kong.
*   **Request Body:** `multipart/form-data` OR `application/json` *(Assumption - Verify)*
    *   Option 1 (`multipart/form-data`):
        *   `file`: (Required) Image file of the receipt.
    *   Option 2 (`application/json`):
        *   `ocr_text`: (Required) Text extracted from a receipt by another OCR service.
        *   `num_people`: (Optional) Number of people to split amongst.
*   **Response (Success - 200 OK):** `application/json` *(Assumption - Verify actual response format)*
    ```json
    {
      "items": [
        {"item": "Burger", "price": 10.50},
        {"item": "Fries", "price": 3.00}
        // ...
      ],
      "total_amount": 13.50,
      "split_details": {
         // Details on how the bill is split if applicable
      }
    }
    ```
*   **Response (Error):** 400, 422, 500.

---

## 💬 7. GigaChat Service

**Base URL (Direct):** `http://localhost:8005` (Default)
**(Access via Kong: `http://localhost:7000/chat/gigachat` - *Example path, configure in Kong*)**

### 💬 7.1. Text Chat

*   **Endpoint:** `POST /chat`
*   **Description:** Send message history for a GigaChat model response. Auth handled internally.
*   **Headers:**
    *   `Content-Type`: `application/json`
*   **Request Body:** `application/json`
    ```json
    {
      "messages": [ /* {"role": "user", "content": "..."}, ... */ ],
      "model": "GigaChat-Pro", // Optional override
      "temperature": 0.7, // Optional
      "max_tokens": 100 // Optional
    }
    ```
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response": {
        "role": "assistant",
        "content": "GigaChat response..."
      },
      "model_used": "GigaChat-Pro",
      "usage": { /* token counts */ }
    }
    ```

---

## ✅ 8. Health Check

All services should provide a health check endpoint. Access via Kong or directly.

*   **Endpoint:** `GET /health` (Usually)
*   **Description:** Returns the operational status of the service.
*   **Response (Success - 200 OK):** `application/json` (Format varies slightly per service)
    ```json
    // Example structure
    {
      "status": "ok"
      // Potentially other fields like "service_name", "version"
    }
    ```
*   **Example (curl via Direct URL):**
    ```bash
    curl http://localhost:8800/health # Auth
    curl http://localhost:8000/health # Gemini
    curl http://localhost:8001/health # Grok
    curl http://localhost:8002/health # Cloud Vision
    curl http://localhost:8003/health # Pytesseract (Verify path)
    curl http://localhost:8004/health # Split Bill (Verify path)
    curl http://localhost:8005/health # GigaChat