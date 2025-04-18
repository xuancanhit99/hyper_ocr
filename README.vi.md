# ✨ API Services OCR & Chat (Gemini, Grok & GigaChat)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án này cung cấp nhiều API service cho chức năng Nhận dạng Ký tự Quang học (OCR) và trò chuyện văn bản, sử dụng các mô hình từ Google Gemini, XAI Grok, và Sber GigaChat.

## ✅ Yêu cầu

*   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Bắt đầu Nhanh

1.  **Clone repository:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Cấu hình API Keys:**
    *   **Gemini:**
        ```bash
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        ```
        Sau đó, sửa tệp `ocr_gemini_service/.env` và thêm `GOOGLE_API_KEY` của bạn.
    *   **Grok:**
        ```bash
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        ```
        Sau đó, sửa tệp `ocr_grok_vision_service/.env` và thêm `XAI_API_KEY` của bạn.
    *   **GigaChat:**
        ```bash
        cp gigachat_service/.env.example gigachat_service/.env
        ```
        Sau đó, sửa tệp `gigachat_service/.env` và thêm `GIGACHAT_AUTH_KEY` của bạn. Bạn cũng có thể cần điều chỉnh `GIGACHAT_SCOPE` dựa trên loại tài khoản của bạn.
    *(Tùy chọn: Bạn cũng có thể tùy chỉnh tên model mặc định và cổng trong các tệp `.env`.)*

3.  **▶️ Chạy các dịch vụ:**
    ```bash
    docker compose up --build -d
    ```
    *   Dịch vụ Gemini sẽ có tại `http://localhost:8000`
    *   Dịch vụ Grok sẽ có tại `http://localhost:8001`
    *   Dịch vụ GigaChat sẽ có tại `http://localhost:8005` (hoặc cổng được chỉ định trong `gigachat_service/.env`)

## 📚 Tài liệu API

*   Hướng dẫn sử dụng chi tiết và ví dụ: [docs/api_usage.vi.md](docs/api_usage.vi.md)
*   Tài liệu tương tác Swagger UI:
    *   Gemini: `http://localhost:8000/docs`
    *   Grok: `http://localhost:8001/docs`
    *   GigaChat: `http://localhost:8005/docs` (hoặc cổng đã cấu hình)

## 📜 Giấy phép

Dự án này được cấp phép theo Giấy phép MIT - xem chi tiết trong tệp [LICENSE](LICENSE).

Bản quyền (c) 2025 MIREA TEAM.