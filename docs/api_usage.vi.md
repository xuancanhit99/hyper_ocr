# 📄 Tài liệu API - Bộ Microservice Hyper OCR

Tài liệu này mô tả cách tích hợp và sử dụng các API được cung cấp bởi các microservice khác nhau trong bộ Hyper OCR, bao gồm các dịch vụ OCR, Chat, Xác thực và Tiện ích.

## ℹ️ Thông tin Chung

### 🌐 Truy cập Dịch vụ

Mặc dù các dịch vụ expose các cổng riêng lẻ trong quá trình phát triển cục bộ, **cách tương tác API được khuyến nghị và tiêu chuẩn là thông qua Kong API Gateway**.

*   **API Gateway Base URL:** `http://localhost:7000`

Kong xử lý việc định tuyến các yêu cầu đến dịch vụ backend thích hợp dựa trên đường dẫn hoặc các quy tắc khác mà bạn cấu hình. Bạn sẽ cần cấu hình Kong (thông qua giao diện Konga tại `http://localhost:7337` hoặc Admin API tại `http://localhost:7001`) để expose các endpoint dịch vụ mong muốn thông qua gateway.

### Base URLs Dịch vụ Trực tiếp (Mặc định - Chỉ dành cho Phát triển/Gỡ lỗi)

*   **Dịch vụ Xác thực (Auth Service):** `http://localhost:8800`
*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`
*   **OCR Cloud Vision Service:** `http://localhost:8002`
*   **OCR Pytesseract Service:** `http://localhost:8003`
*   **Dịch vụ Chia hóa đơn (Split Bill Service):** `http://localhost:8004`
*   **GigaChat Service:** `http://localhost:8005` (Mặc định, kiểm tra `gigachat_service/.env`)

*(Lưu ý: Truy cập trực tiếp có thể bị vô hiệu hóa hoặc các cổng có thể thay đổi tùy thuộc vào cấu hình triển khai. Luôn ưu tiên sử dụng API Gateway.)*

### 🔑 Xác thực (Authentication)

Phương thức xác thực khác nhau tùy theo dịch vụ và cách chúng được expose qua Kong:

*   **Dịch vụ Xác thực:** Có khả năng sử dụng JWT Bearer token. Lấy token thông qua một endpoint đăng nhập (ví dụ: `/auth/token`) và gửi nó trong header `Authorization: Bearer <token>` cho các endpoint được bảo vệ.
*   **Dịch vụ Gemini & Grok:** Có thể sử dụng xác thực dựa trên API Key thông qua HTTP Header `X-API-Key` (Google API Key cho Gemini, XAI API Key cho Grok) *nếu không được cấu hình phía máy chủ*. Nếu khóa nằm trong tệp `.env` của dịch vụ, không cần header khi truy cập trực tiếp. Kong có thể được cấu hình để quản lý hoặc chèn các khóa này.
*   **Dịch vụ GigaChat:** Xử lý xác thực nội bộ bằng OAuth 2.0 được cấu hình qua tệp `.env`. Thường không yêu cầu header xác thực cụ thể khi gọi trực tiếp các endpoint của nó hoặc qua Kong (trừ khi Kong thêm lớp riêng).
*   **Dịch vụ Cloud Vision:** Xác thực bằng Google Cloud Application Default Credentials (ADC) được cấu hình phía máy chủ (ví dụ: biến môi trường `GOOGLE_APPLICATION_CREDENTIALS`). Thường không yêu cầu header HTTP cụ thể.
*   **Dịch vụ Pytesseract:** Có khả năng không yêu cầu xác thực cụ thể.
*   **Dịch vụ Chia hóa đơn:** Có khả năng không yêu cầu xác thực cụ thể, nhưng có thể được bảo vệ thông qua Dịch vụ Xác thực qua Kong.
*   **Kong Gateway:** Bản thân Kong có thể thêm các lớp xác thực (ví dụ: API Keys, JWT, OAuth2) vào bất kỳ route nào, bất kể xác thực riêng của dịch vụ backend. Kiểm tra cấu hình của Kong.

---

## 🔐 1. Dịch vụ Xác thực (Auth Service)

**Base URL (Trực tiếp):** `http://localhost:8800`
**(Truy cập qua Kong: `http://localhost:7000/auth` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

*(Lưu ý: Các endpoint dưới đây là ví dụ và cần xác minh dựa trên triển khai thực tế)*

### 🔑 1.1. Lấy Access Token

*   **Endpoint:** `POST /auth/token`
*   **Mô tả:** Xác thực thông tin đăng nhập của người dùng để nhận JWT access token.
*   **Request Body:** `application/x-www-form-urlencoded`
    *   `username`: Email hoặc tên người dùng.
    *   `password`: Mật khẩu người dùng.
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "access_token": "your_jwt_token_here",
      "token_type": "bearer"
    }
    ```
*   **Response (Lỗi):** 401 Unauthorized, 422 Unprocessable Entity.

### 👤 1.2. Lấy Thông tin Người dùng Hiện tại

*   **Endpoint:** `GET /users/me`
*   **Mô tả:** Lấy chi tiết về người dùng hiện đang được xác thực.
*   **Headers:**
    *   `Authorization`: `Bearer <your_jwt_token_here>`
*   **Response (Thành công - 200 OK):** `application/json` (Schema chi tiết người dùng)
*   **Response (Lỗi):** 401 Unauthorized.

### ➕ 1.3. Đăng ký Người dùng Mới

*   **Endpoint:** `POST /users/`
*   **Mô tả:** Tạo tài khoản người dùng mới.
*   **Request Body:** `application/json` (Schema tạo người dùng, ví dụ: email, password)
*   **Response (Thành công - 201 Created):** `application/json` (Chi tiết người dùng đã tạo)
*   **Response (Lỗi):** 400 Bad Request, 422 Unprocessable Entity.

---

## ♊ 2. OCR Gemini Service

**Base URL (Trực tiếp):** `http://localhost:8000`
**(Truy cập qua Kong: `http://localhost:7000/ocr/gemini` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 📸 2.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên tệp hình ảnh để trích xuất văn bản bằng mô hình Gemini Vision.
*   **Headers:**
    *   `X-API-Key`: (Tùy chọn) Google API Key (nếu không đặt ở phía máy chủ).
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh (JPEG, PNG, WEBP, HEIC, HEIF).
*   **Query Parameters:**
    *   `prompt`: (Tùy chọn) Hướng dẫn mô hình (ví dụ: "Chỉ trích xuất địa chỉ").
    *   `model_name`: (Tùy chọn) Ghi đè model Gemini Vision mặc định.
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "filename": "image.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Văn bản được trích xuất...",
      "model_used": "gemini-pro-vision"
    }
    ```
*   **Ví dụ (curl qua Kong):**
    ```bash
    # Giả sử route Kong /ocr/gemini ánh xạ tới dịch vụ này
    curl -X POST "http://localhost:7000/ocr/gemini/ocr/extract-text?prompt=Address" \
         -H "Authorization: Bearer <KONG_JWT_IF_NEEDED>" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \ # Nếu được yêu cầu bởi Kong hoặc dịch vụ
         -F "file=@/duong/dan/toi/anh.png"
    ```

### 💬 2.2. Trò chuyện Văn bản (Chat)

*   **Endpoint:** `POST /chat/`
*   **Mô tả:** Gửi tin nhắn và lịch sử để nhận phản hồi từ mô hình Gemini Text.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Tùy chọn) Google API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "Tin nhắn của người dùng",
      "history": [ /* {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."} */ ],
      "model_name": "gemini-pro" // Tùy chọn ghi đè
    }
    ```
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Phản hồi của mô hình...",
      "model_used": "gemini-pro"
    }
    ```

---

## 🤖 3. OCR Grok Vision Service

**Base URL (Trực tiếp):** `http://localhost:8001`
**(Truy cập qua Kong: `http://localhost:7000/ocr/grok` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 📸 3.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên tệp hình ảnh để trích xuất văn bản bằng mô hình Grok Vision.
*   **Headers:**
    *   `X-API-Key`: (Tùy chọn) XAI API Key (nếu không đặt ở phía máy chủ).
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh (JPEG, PNG).
*   **Query Parameters:**
    *   `prompt`: (Tùy chọn) Hướng dẫn mô hình.
    *   `model_name`: (Tùy chọn) Ghi đè model Grok Vision mặc định.
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "filename": "image.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Văn bản được trích xuất...",
      "model_used": "grok-1.5-vision-preview"
    }
    ```

### 💬 3.2. Trò chuyện Văn bản (Chat)

*   **Endpoint:** `POST /chat/`
*   **Mô tả:** Gửi tin nhắn và lịch sử để nhận phản hồi từ mô hình Grok Text.
*   **Headers:**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Tùy chọn) XAI API Key.
*   **Request Body:** `application/json`
    ```json
    {
      "message": "Tin nhắn của người dùng",
      "history": [ /* ... */ ],
      "model_name": "grok-1.5-flash" // Tùy chọn ghi đè
    }
    ```
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Phản hồi của mô hình...",
      "model_used": "grok-1.5-flash"
    }
    ```

---

## ☁️ 4. OCR Cloud Vision Service

**Base URL (Trực tiếp):** `http://localhost:8002`
**(Truy cập qua Kong: `http://localhost:7000/ocr/cloud-vision` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 📸 4.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text`
*   **Mô tả:** Tải lên tệp hình ảnh để OCR bằng Google Cloud Vision API.
*   **Xác thực:** Sử dụng ADC phía máy chủ. Thường không cần header cụ thể.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh (JPEG, PNG, GIF, BMP, WEBP, RAW, ICO, PDF, TIFF).
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "text": "Toàn bộ văn bản được trích xuất...",
      "details": [
        {
          "text": "Từ 1",
          "bounding_box": [ /* {"x": ..., "y": ...} */ ]
        }
        // ... các khối được phát hiện khác
      ]
    }
    ```

---

## 📄 5. OCR Pytesseract Service

**Base URL (Trực tiếp):** `http://localhost:8003`
**(Truy cập qua Kong: `http://localhost:7000/ocr/tesseract` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 📸 5.1. Trích xuất Văn bản từ Hình ảnh (OCR)

*   **Endpoint:** `POST /ocr/extract-text` *(Giả định - Xác minh endpoint thực tế)*
*   **Mô tả:** Tải lên tệp hình ảnh để OCR bằng engine Tesseract.
*   **Xác thực:** Có khả năng không yêu cầu trực tiếp.
*   **Request Body:** `multipart/form-data`
    *   `file`: (Bắt buộc) Tệp hình ảnh (Các định dạng phổ biến như PNG, JPEG, TIFF).
*   **Query Parameters:**
    *   `lang`: (Tùy chọn) Mã ngôn ngữ cho Tesseract (ví dụ: `eng`, `vie`, `eng+vie`). Mặc định có thể được cấu hình phía máy chủ.
*   **Response (Thành công - 200 OK):** `application/json` *(Giả định - Xác minh định dạng phản hồi thực tế)*
    ```json
    {
      "extracted_text": "Văn bản được trích xuất bởi Tesseract...",
      "language_used": "vie" // Ví dụ
    }
    ```
*   **Response (Lỗi):** 400, 422, 500.

---

## 💸 6. Dịch vụ Chia hóa đơn (Split Bill Service)

**Base URL (Trực tiếp):** `http://localhost:8004`
**(Truy cập qua Kong: `http://localhost:7000/split-bill` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 🧾 6.1. Chia hóa đơn từ Hình ảnh hoặc Văn bản

*   **Endpoint:** `POST /split-bill/` *(Giả định - Xác minh endpoint thực tế)*
*   **Mô tả:** Phân tích hình ảnh (thường là hóa đơn) hoặc văn bản được cung cấp để xác định các mục và có khả năng chia chi phí.
*   **Xác thực:** Có thể yêu cầu xác thực (ví dụ: JWT qua Dịch vụ Xác thực) tùy thuộc vào cấu hình qua Kong.
*   **Request Body:** `multipart/form-data` HOẶC `application/json` *(Giả định - Xác minh)*
    *   Lựa chọn 1 (`multipart/form-data`):
        *   `file`: (Bắt buộc) Tệp hình ảnh của hóa đơn.
    *   Lựa chọn 2 (`application/json`):
        *   `ocr_text`: (Bắt buộc) Văn bản được trích xuất từ hóa đơn bởi một dịch vụ OCR khác.
        *   `num_people`: (Tùy chọn) Số người để chia.
*   **Response (Thành công - 200 OK):** `application/json` *(Giả định - Xác minh định dạng phản hồi thực tế)*
    ```json
    {
      "items": [
        {"item": "Bánh mì kẹp", "price": 10.50},
        {"item": "Khoai tây chiên", "price": 3.00}
        // ...
      ],
      "total_amount": 13.50,
      "split_details": {
         // Chi tiết về cách chia hóa đơn nếu có
      }
    }
    ```
*   **Response (Lỗi):** 400, 422, 500.

---

## 💬 7. GigaChat Service

**Base URL (Trực tiếp):** `http://localhost:8005` (Mặc định)
**(Truy cập qua Kong: `http://localhost:7000/chat/gigachat` - *Đường dẫn ví dụ, cấu hình trong Kong*)**

### 💬 7.1. Trò chuyện Văn bản (Chat)

*   **Endpoint:** `POST /chat`
*   **Mô tả:** Gửi lịch sử tin nhắn để nhận phản hồi từ mô hình GigaChat. Xác thực được xử lý nội bộ.
*   **Headers:**
    *   `Content-Type`: `application/json`
*   **Request Body:** `application/json`
    ```json
    {
      "messages": [ /* {"role": "user", "content": "..."}, ... */ ],
      "model": "GigaChat-Pro", // Tùy chọn ghi đè
      "temperature": 0.7, // Tùy chọn
      "max_tokens": 100 // Tùy chọn
    }
    ```
*   **Response (Thành công - 200 OK):** `application/json`
    ```json
    {
      "response": {
        "role": "assistant",
        "content": "Phản hồi của GigaChat..."
      },
      "model_used": "GigaChat-Pro",
      "usage": { /* số lượng token */ }
    }
    ```

---

## ✅ 8. Health Check

Tất cả các dịch vụ nên cung cấp một endpoint kiểm tra tình trạng. Truy cập qua Kong hoặc trực tiếp.

*   **Endpoint:** `GET /health` (Thường là vậy)
*   **Mô tả:** Trả về trạng thái hoạt động của dịch vụ.
*   **Response (Thành công - 200 OK):** `application/json` (Định dạng thay đổi một chút tùy dịch vụ)
    ```json
    // Cấu trúc ví dụ
    {
      "status": "ok"
      // Có thể có các trường khác như "service_name", "version"
    }
    ```
*   **Ví dụ (curl qua URL Trực tiếp):**
    ```bash
    curl http://localhost:8800/health # Auth
    curl http://localhost:8000/health # Gemini
    curl http://localhost:8001/health # Grok
    curl http://localhost:8002/health # Cloud Vision
    curl http://localhost:8003/health # Pytesseract (Xác minh đường dẫn)
    curl http://localhost:8004/health # Split Bill (Xác minh đường dẫn)
    curl http://localhost:8005/health # GigaChat