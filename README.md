# ✨ Hyper OCR - Microservices Suite (OCR, Chat, Auth, API Gateway & More)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides a suite of microservices including:
*   **OCR Services:** Leveraging Google Gemini, XAI Grok, Google Cloud Vision, and Tesseract.
*   **Chat Service:** Utilizing Sber GigaChat.
*   **Utility Service:** Splitting bills based on OCR results.
*   **Authentication Service:** Managing user authentication and authorization.
*   **API Gateway:** Kong for managing, securing, and routing API requests.
*   **Monitoring:** Prometheus, Grafana, and Uptime Kuma for observing service health and performance.

## ✅ Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Configure API Keys & Environment:**
    *   Copy the example environment files for the services you intend to use:
        ```bash
        # Core Services
        cp auth_service/.env.example auth_service/.env
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        cp ocr_cloud_vision_service/.env.example ocr_cloud_vision_service/.env
        # cp ocr_pytesseract_service/.env.example ocr_pytesseract_service/.env # No .env.example found, check service requirements
        cp gigachat_service/.env.example gigachat_service/.env
        # cp split_bill_service/.env.example split_bill_service/.env       # No .env.example found, check service requirements

        # Infrastructure (Optional: review defaults in compose.yaml)
        # Kong, Konga, Prometheus, Grafana, Uptime Kuma configurations are primarily in compose.yaml or specific config files (e.g., monitoring/prometheus.yml)
        ```
    *   **Edit the `.env` files** and add your necessary API keys, credentials, or custom settings:
        *   `auth_service/.env`: Configure database connection, secrets, etc.
        *   `ocr_gemini_service/.env`: Add `GOOGLE_API_KEY`.
        *   `ocr_grok_vision_service/.env`: Add `XAI_API_KEY`.
        *   `ocr_cloud_vision_service/.env`: Configure Google Cloud credentials (e.g., `GOOGLE_APPLICATION_CREDENTIALS` path if mounting).
        *   `gigachat_service/.env`: Add `GIGACHAT_AUTH_KEY` and optionally adjust `GIGACHAT_SCOPE`, `GIGACHAT_SERVICE_PORT`.
    *(Note: For services without an `.env.example`, check their respective directories or documentation for required environment variables.)*

3.  **▶️ Run the services:**
    ```bash
    docker compose up --build -d
    ```
    *   The services will start. Access them through the Kong API Gateway (recommended) or directly via their exposed ports.

## 📚 API & Service Access

*   **API Gateway (Kong):** `http://localhost:7000` (Proxy), `http://localhost:7001` (Admin API)
*   **Gateway Admin UI (Konga):** `http://localhost:7337`
*   **Monitoring:**
    *   Prometheus: `http://localhost:9090`
    *   Grafana: `http://localhost:3000` (Default login: admin/admin - CHANGE THIS)
    *   Uptime Kuma: `http://localhost:3001`
*   **Direct Service Access & Swagger UI (if available):**
    *   Auth Service: `http://localhost:8800` (Docs: `http://localhost:8800/docs` or `/api/docs` - verify path)
    *   Gemini OCR: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
    *   Grok Vision OCR: `http://localhost:8001` (Docs: `http://localhost:8001/docs`)
    *   Cloud Vision OCR: `http://localhost:8002` (Docs: `http://localhost:8002/docs`)
    *   Pytesseract OCR: `http://localhost:8003` (Docs: `http://localhost:8003/docs`)
    *   Split Bill: `http://localhost:8004` (Docs: `http://localhost:8004/docs`)
    *   GigaChat: `http://localhost:8005` (or configured port) (Docs: `http://localhost:8005/docs`)

*   **Detailed API Usage:** See [docs/api_usage.md](docs/api_usage.md) for examples (needs update for new services).

## 🔧 Configuration & Management

*   **API Gateway (Kong):** Configure routes, services, plugins, consumers, etc., via the Admin API (`:7001`) or Konga UI (`:7337`).
*   **Monitoring:** Configure Prometheus targets in `monitoring/prometheus.yml`. Build dashboards in Grafana. Set up monitors in Uptime Kuma.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 MIREA TEAM.