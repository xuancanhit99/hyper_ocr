# 📄 Tài liệu API - Dịch vụ OCR và Chat (Gemini & Grok)

Tài liệu này mô tả cách tích hợp và sử dụng các API được cung cấp bởi dịch vụ OCR Gemini và OCR Grok Vision.

## ℹ️ Thông tin Chung

### Base URLs (Mặc định khi chạy qua Docker Compose)

*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`

*(Lưu ý: Các cổng này có thể thay đổi tùy thuộc vào cấu hình triển khai của bạn)*

### 🔑 Xác thực (Authentication)

Cả hai dịch vụ đều sử dụng xác thực dựa trên API Key thông qua HTTP Header.

*   **Header Name:** `X-API-Key`
*   **Value:** Khóa API tương ứng (Google API Key cho Gemini, XAI API Key cho Grok).

Nếu khóa API đã được cấu hình trong tệp `.env` của dịch vụ phía máy chủ, bạn không cần gửi header này. Nếu bạn muốn ghi đè hoặc cung cấp khóa API cho mỗi yêu cầu, hãy sử dụng header này.

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

## ✅ 3. Health Check

Cả hai dịch vụ đều cung cấp một endpoint để kiểm tra trạng thái hoạt động.

*   **Endpoint:** `GET /health/`
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
*   **Ví dụ (curl):**
    ```bash
    curl -X GET http://localhost:8000/health/
    curl -X GET http://localhost:8001/health/