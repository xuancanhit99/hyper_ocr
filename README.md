# ✨ OCR & Chat API Services (Gemini, Grok & GigaChat)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides multiple API services for Optical Character Recognition (OCR) and text-based chat functionalities, leveraging models from Google Gemini, XAI Grok, and Sber GigaChat.

## ✅ Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Configure API Keys:**
    *   **Gemini:**
        ```bash
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        ```
        Then, edit `ocr_gemini_service/.env` and add your `GOOGLE_API_KEY`.
    *   **Grok:**
        ```bash
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        ```
        Then, edit `ocr_grok_vision_service/.env` and add your `XAI_API_KEY`.
    *   **GigaChat:**
        ```bash
        cp gigachat_service/.env.example gigachat_service/.env
        ```
        Then, edit `gigachat_service/.env` and add your `GIGACHAT_AUTH_KEY`. You might also need to adjust `GIGACHAT_SCOPE` based on your account type.
    *(Optional: You can also customize default model names and ports in the `.env` files.)*

3.  **▶️ Run the services:**
    ```bash
    docker compose up --build -d
    ```
    *   Gemini service will be available at `http://localhost:8000`
    *   Grok service will be available at `http://localhost:8001`
    *   GigaChat service will be available at `http://localhost:8005` (or the port specified in `gigachat_service/.env`)

## 📚 API Documentation

*   Detailed usage instructions and examples: [docs/api_usage.md](docs/api_usage.md)
*   Interactive Swagger UI:
    *   Gemini: `http://localhost:8000/docs`
    *   Grok: `http://localhost:8001/docs`
    *   GigaChat: `http://localhost:8005/docs` (or the configured port)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 MIREA TEAM.