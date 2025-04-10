# 📄 Tài liệu API - Dịch vụ OCR và Chat (Gemini, Grok, Cloud Vision)

Tài liệu này mô tả cách tích hợp và sử dụng các API được cung cấp bởi dịch vụ OCR Gemini, OCR Grok Vision và OCR Cloud Vision.

## ℹ️ Thông tin Chung

### Base URLs (Mặc định khi chạy qua Docker Compose)

*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`
*   **OCR Cloud Vision Service:** `http://localhost:8002`

*(Lưu ý: Các cổng này có thể thay đổi tùy thuộc vào cấu hình triển khai của bạn)*

### 🔑 Xác thực (Authentication)

*   **Dịch vụ Gemini & Grok:** Các dịch vụ này có thể sử dụng xác thực dựa trên API Key thông qua HTTP Header `X-API-Key` (Google API Key cho Gemini, XAI API Key cho Grok). Nếu khóa API đã được cấu hình trong tệp `.env` của dịch vụ phía máy chủ, bạn không cần gửi header này. Chỉ sử dụng header này nếu bạn muốn ghi đè hoặc cung cấp khóa API cho mỗi yêu cầu.
*   **Dịch vụ Cloud Vision:** Dịch vụ này xác thực bằng Google Cloud Application Default Credentials (ADC). Thông thường, điều này bao gồm việc đặt biến môi trường `GOOGLE_APPLICATION_CREDENTIALS` trong môi trường của dịch vụ (ví dụ: qua tệp `.env` và Docker Compose) để trỏ đến tệp khóa tài khoản dịch vụ (service account key file). Thường không cần header HTTP cụ thể nào để xác thực khi sử dụng ADC.

---

## ♊ 1. OCR Gemini Service

**Base URL:** `http://localhost:8000`

### 📸 1.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên một tệp hình ảnh để trích xuất văn bản bằng mô hình Gemini Vision.
*   **Headers:**
    *   `X-API-Key`: (Tùy chọn) Google API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh cần xử lý (Các loại được phép: `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`).
*   **Query Parameters:**
    *   `prompt`: (Tùy chọn) Chuỗi văn bản để hướng dẫn mô hình (ví dụ: "Chỉ trích xuất địa chỉ"). Mặc định là trích xuất tất cả văn bản.
    *   `model_name`: (Tùy chọn) Tên model Gemini Vision cụ thể muốn sử dụng (ví dụ: `gemini-2.0-flash-exp-image-generation`). Mặc định được lấy từ cấu hình (`GEMINI_VISION_MODEL_NAME`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "ten_file_anh.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Nội dung văn bản được trích xuất...",
      "model_used": "gemini-2.0-flash-exp-image-generation" // Ví dụ model đã dùng
    }
    ```
*   **Response (Error):** `application/json` (Ví dụ: 400, 422, 500, 503)
    ```json
    {
      "detail": "Mô tả lỗi chi tiết..."
    }
    ```
*   **Ví dụ (curl):**
    ```bash
    curl -X POST "http://localhost:8000/ocr/extract-text?prompt=Extract%20only%20the%20invoice%20number&model_name=gemini-2.0-flash-exp-image-generation" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -F "file=@/duong/dan/toi/file/anh.png"
    ```

### 💬 1.2. Trò chuyện Văn bản (Chat)

*   **Endpoint:** `POST /chat/`
*   **Mô tả:** Gửi tin nhắn và lịch sử trò chuyện để nhận phản hồi từ mô hình Gemini Text.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Tùy chọn) Google API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "Tin nhắn mới của người dùng",
      "history": [
        {"role": "user", "content": "Tin nhắn trước đó của người dùng"},
        {"role": "assistant", "content": "Phản hồi trước đó của mô hình"}
        // ... các lượt khác
      ],
      "model_name": "gemini-2.0-flash" // Tùy chọn: ghi đè model mặc định (vd: dùng flash cho chat)
    }
    ```
    *   `message`: (Bắt buộc) Tin nhắn mới nhất từ người dùng.
    *   `history`: (Tùy chọn) Danh sách các tin nhắn trước đó. `role` phải là `"user"` hoặc `"assistant"`.
    *   `model_name`: (Tùy chọn) Tên model Gemini Text cụ thể muốn sử dụng (ví dụ: `gemini-2.0-flash`). Mặc định được lấy từ cấu hình (`GEMINI_TEXT_MODEL_NAME`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Phản hồi từ mô hình Gemini...",
      "model_used": "gemini-2.0-flash" // Ví dụ model đã dùng
    }
    ```
*   **Response (Error):** `application/json` (Ví dụ: 400, 500, 503)
    ```json
    {
      "detail": "Mô tả lỗi chi tiết..."
    }
    ```
*   **Ví dụ (curl):**
    ```bash
    curl -X POST "http://localhost:8000/chat/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -d '{
               "message": "Thủ đô của Pháp là gì?",
               "history": [
                 {"role": "user", "content": "Xin chào"},
                 {"role": "assistant", "content": "Chào bạn!"}
               ],
               "model_name": "gemini-2.0-flash"
             }'
    ```

---

## 🤖 2. OCR Grok Vision Service

**Base URL:** `http://localhost:8001`

### 📸 2.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên một tệp hình ảnh để trích xuất văn bản bằng mô hình Grok Vision.
*   **Headers:**
    *   `X-API-Key`: (Tùy chọn) XAI API Key.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh cần xử lý (Các loại được phép: `image/jpeg`, `image/png`).
*   **Query Parameters:**
    *   `prompt`: (Tùy chọn) Chuỗi văn bản để hướng dẫn mô hình. Mặc định là trích xuất tất cả văn bản.
    *   `model_name`: (Tùy chọn) Tên model Grok Vision cụ thể muốn sử dụng (ví dụ: `grok-2-vision-1212`). Mặc định được lấy từ cấu hình (`GROK_VISION_DEFAULT_MODEL`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "filename": "ten_file_anh.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Nội dung văn bản được trích xuất...",
      "model_used": "grok-2-vision-1212" // Ví dụ model đã dùng
    }
    ```
*   **Response (Error):** `application/json` (Ví dụ: 400, 415, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Mô tả lỗi chi tiết..."
    }
    ```
*   **Ví dụ (curl):**
    ```bash
    curl -X POST "http://localhost:8001/ocr/extract-text?model_name=grok-2-vision-1212" \
         -H "X-API-Key: YOUR_XAI_API_KEY" \
         -F "file=@/duong/dan/toi/file/anh.jpg"
    ```

### 💬 2.2. Trò chuyện Văn bản (Chat)

*   **Endpoint:** `POST /chat/`
*   **Mô tả:** Gửi tin nhắn và lịch sử trò chuyện để nhận phản hồi từ mô hình Grok Text.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Tùy chọn) XAI API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "Tin nhắn mới của người dùng",
      "history": [
        {"role": "user", "content": "Tin nhắn trước đó của người dùng"},
        {"role": "assistant", "content": "Phản hồi trước đó của mô hình"}
        // ... các lượt khác
      ],
      "model_name": "grok-2-1212" // Tùy chọn: ghi đè model mặc định (vd: dùng grok-2 cho chat)
    }
    ```
    *   `message`: (Bắt buộc) Tin nhắn mới nhất từ người dùng.
    *   `history`: (Tùy chọn) Danh sách các tin nhắn trước đó. `role` phải là `"user"` hoặc `"assistant"`.
    *   `model_name`: (Tùy chọn) Tên model Grok Text cụ thể muốn sử dụng (ví dụ: `grok-2-1212`). Mặc định được lấy từ cấu hình (`GROK_TEXT_DEFAULT_MODEL`).
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Phản hồi từ mô hình Grok...",
      "model_used": "grok-2-1212" // Ví dụ model đã dùng
    }
    ```
*   **Response (Error):** `application/json` (Ví dụ: 400, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Mô tả lỗi chi tiết..."
    }
    ```
*   **Ví dụ (curl):**
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

## ☁️ 3. OCR Cloud Vision Service

**Base URL:** `http://localhost:8002`

### 📸 3.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên một tệp hình ảnh để trích xuất văn bản bằng Google Cloud Vision API.
*   **Xác thực:** Sử dụng Google Cloud Application Default Credentials (ADC) được cấu hình phía máy chủ (thông qua biến môi trường `GOOGLE_APPLICATION_CREDENTIALS`). Không cần header `X-API-Key` cụ thể.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh cần xử lý (Hỗ trợ nhiều định dạng như JPEG, PNG, GIF, BMP, WEBP, RAW, ICO, PDF, TIFF - kiểm tra tài liệu Google Cloud Vision để biết danh sách đầy đủ và giới hạn).
*   **Query Parameters:** Không có.
*   **Response (Success - 200 OK):** `application/json`
    ```json
    {
      "text": "Nội dung văn bản đầy đủ được trích xuất...",
      "details": [
        {
          "text": "Từ 1",
          "bounding_box": [
            {"x": 10, "y": 10},
            {"x": 50, "y": 10},
            {"x": 50, "y": 30},
            {"x": 10, "y": 30}
          ]
        },
        {
          "text": "Từ 2",
          "bounding_box": [
            {"x": 60, "y": 10},
            {"x": 100, "y": 10},
            {"x": 100, "y": 30},
            {"x": 60, "y": 30}
          ]
        }
        // ... các khối văn bản khác được phát hiện
      ]
    }
    ```
*   **Response (Error):** `application/json` (Ví dụ: 400, 403, 429, 500, 502)
    ```json
    {
      "detail": "Mô tả lỗi chi tiết (ví dụ: 'Permission denied: Check credentials/API key permissions...', 'API quota exceeded...', 'Invalid image format or content...', 'Upstream Google API Error:...')"
    }
    ```
*   **Ví dụ (curl):**
    ```bash
    curl -X POST "http://localhost:8002/ocr/extract-text" \
         -F "file=@/duong/dan/toi/file/anh.png"
    ```

---

## ✅ 4. Health Check

Tất cả các dịch vụ đều cung cấp một endpoint để kiểm tra trạng thái hoạt động.

*   **Endpoint:** `GET /health` (Lưu ý: Không có dấu gạch chéo cuối cho Cloud Vision)
*   **Mô tả:** Trả về trạng thái hiện tại của dịch vụ.
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
    *   *Cloud Vision:*
        ```json
        {
          "status": "ok"
        }
        ```
*   **Ví dụ (curl):**
    ```bash
    curl -X GET http://localhost:8000/health/
    curl -X GET http://localhost:8001/health/
    curl -X GET http://localhost:8002/health