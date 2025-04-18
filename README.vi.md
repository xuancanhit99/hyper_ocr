# ✨ Bộ Microservice Hyper OCR (OCR, Chat, Auth, API Gateway & Hơn thế nữa)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án này cung cấp một bộ microservice bao gồm:
*   **Dịch vụ OCR:** Sử dụng Google Gemini, XAI Grok, Google Cloud Vision, và Tesseract.
*   **Dịch vụ Chat:** Sử dụng Sber GigaChat.
*   **Dịch vụ Tiện ích:** Chia hóa đơn dựa trên kết quả OCR.
*   **Dịch vụ Xác thực:** Quản lý xác thực và ủy quyền người dùng.
*   **API Gateway:** Kong để quản lý, bảo mật và định tuyến các yêu cầu API.
*   **Giám sát:** Prometheus, Grafana, và Uptime Kuma để quan sát tình trạng và hiệu suất của dịch vụ.

## ✅ Yêu cầu

*   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Bắt đầu Nhanh

1.  **Clone repository:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Cấu hình API Keys & Môi trường:**
    *   Sao chép các tệp môi trường mẫu cho các dịch vụ bạn dự định sử dụng:
        ```bash
        # Các dịch vụ cốt lõi
        cp auth_service/.env.example auth_service/.env
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        cp ocr_cloud_vision_service/.env.example ocr_cloud_vision_service/.env
        # cp ocr_pytesseract_service/.env.example ocr_pytesseract_service/.env # Không tìm thấy .env.example, kiểm tra yêu cầu dịch vụ
        cp gigachat_service/.env.example gigachat_service/.env
        # cp split_bill_service/.env.example split_bill_service/.env       # Không tìm thấy .env.example, kiểm tra yêu cầu dịch vụ

        # Hạ tầng (Tùy chọn: xem lại cấu hình mặc định trong compose.yaml)
        # Cấu hình Kong, Konga, Prometheus, Grafana, Uptime Kuma chủ yếu nằm trong compose.yaml hoặc các tệp cấu hình cụ thể (ví dụ: monitoring/prometheus.yml)
        ```
    *   **Chỉnh sửa các tệp `.env`** và thêm các API key, thông tin đăng nhập cần thiết hoặc cài đặt tùy chỉnh:
        *   `auth_service/.env`: Cấu hình kết nối cơ sở dữ liệu, secrets, v.v.
        *   `ocr_gemini_service/.env`: Thêm `GOOGLE_API_KEY`.
        *   `ocr_grok_vision_service/.env`: Thêm `XAI_API_KEY`.
        *   `ocr_cloud_vision_service/.env`: Cấu hình thông tin đăng nhập Google Cloud (ví dụ: đường dẫn `GOOGLE_APPLICATION_CREDENTIALS` nếu mount).
        *   `gigachat_service/.env`: Thêm `GIGACHAT_AUTH_KEY` và tùy chọn điều chỉnh `GIGACHAT_SCOPE`, `GIGACHAT_SERVICE_PORT`.
    *(Lưu ý: Đối với các dịch vụ không có `.env.example`, hãy kiểm tra thư mục tương ứng hoặc tài liệu của chúng để biết các biến môi trường bắt buộc.)*

3.  **▶️ Chạy các dịch vụ:**
    ```bash
    docker compose up --build -d
    ```
    *   Các dịch vụ sẽ khởi động. Truy cập chúng thông qua Kong API Gateway (khuyến nghị) hoặc trực tiếp qua các cổng được expose.

## 📚 Tài liệu API & Truy cập Dịch vụ

*   **API Gateway (Kong):** `http://localhost:7000` (Proxy), `http://localhost:7001` (Admin API)
*   **Giao diện quản trị Gateway (Konga):** `http://localhost:7337`
*   **Giám sát:**
    *   Prometheus: `http://localhost:9090`
    *   Grafana: `http://localhost:3000` (Đăng nhập mặc định: admin/admin - HÃY THAY ĐỔI)
    *   Uptime Kuma: `http://localhost:3001`
*   **Truy cập trực tiếp Dịch vụ & Swagger UI (nếu có):**
    *   Dịch vụ Xác thực: `http://localhost:8800` (Docs: `http://localhost:8800/docs` hoặc `/api/docs` - xác minh đường dẫn)
    *   Gemini OCR: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
    *   Grok Vision OCR: `http://localhost:8001` (Docs: `http://localhost:8001/docs`)
    *   Cloud Vision OCR: `http://localhost:8002` (Docs: `http://localhost:8002/docs`)
    *   Pytesseract OCR: `http://localhost:8003` (Docs: `http://localhost:8003/docs`)
    *   Chia hóa đơn: `http://localhost:8004` (Docs: `http://localhost:8004/docs`)
    *   GigaChat: `http://localhost:8005` (hoặc cổng đã cấu hình) (Docs: `http://localhost:8005/docs`)

*   **Hướng dẫn sử dụng API chi tiết:** Xem [docs/api_usage.vi.md](docs/api_usage.vi.md) để biết ví dụ (cần cập nhật cho các dịch vụ mới).

## 🔧 Cấu hình & Quản lý

*   **API Gateway (Kong):** Cấu hình routes, services, plugins, consumers, v.v., thông qua Admin API (`:7001`) hoặc giao diện Konga (`:7337`).
*   **Giám sát:** Cấu hình các target Prometheus trong `monitoring/prometheus.yml`. Xây dựng dashboards trong Grafana. Thiết lập các monitor trong Uptime Kuma.

## 📜 Giấy phép

Dự án này được cấp phép theo Giấy phép MIT - xem chi tiết trong tệp [LICENSE](LICENSE).

Bản quyền (c) 2025 MIREA TEAM.