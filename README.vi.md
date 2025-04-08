# API Services OCR & Chat (Gemini & Grok)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án này cung cấp hai API service riêng biệt cho chức năng Nhận dạng Ký tự Quang học (OCR) và trò chuyện văn bản, sử dụng các mô hình từ Google Gemini và XAI Grok.

## Yêu cầu

*   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## Bắt đầu Nhanh

1.  **Clone repository:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **Cấu hình API Keys:**
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
    *(Tùy chọn: Bạn cũng có thể tùy chỉnh tên model mặc định trong các tệp `.env`.)*

3.  **Chạy các dịch vụ:**
    ```bash
    docker compose up --build -d
    ```
    *   Dịch vụ Gemini sẽ có tại `http://localhost:8000`
    *   Dịch vụ Grok sẽ có tại `http://localhost:8001`

## Tài liệu API

*   Hướng dẫn sử dụng chi tiết và ví dụ: [docs/api_usage.vi.md](docs/api_usage.vi.md)
*   Tài liệu tương tác Swagger UI:
    *   Gemini: `http://localhost:8000/docs`
    *   Grok: `http://localhost:8001/docs`

## Giấy phép

Dự án này được cấp phép theo Giấy phép MIT - xem chi tiết trong tệp [LICENSE](LICENSE).

Bản quyền (c) 2025 MIREA TEAM.