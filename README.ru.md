# ✨ API-сервисы OCR и Чата (Gemini, Grok & GigaChat)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Этот проект предоставляет несколько API-сервисов для оптического распознавания символов (OCR) и текстового чата, использующих модели от Google Gemini, XAI Grok и Sber GigaChat.

## ✅ Требования

*   [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Быстрый старт

1.  **Клонировать репозиторий:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Настроить ключи API:**
    *   **Gemini:**
        ```bash
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        ```
        Затем отредактируйте файл `ocr_gemini_service/.env` и добавьте ваш `GOOGLE_API_KEY`.
    *   **Grok:**
        ```bash
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        ```
        Затем отредактируйте файл `ocr_grok_vision_service/.env` и добавьте ваш `XAI_API_KEY`.
    *   **GigaChat:**
        ```bash
        cp gigachat_service/.env.example gigachat_service/.env
        ```
        Затем отредактируйте файл `gigachat_service/.env` и добавьте ваш `GIGACHAT_AUTH_KEY`. Вам также может потребоваться изменить `GIGACHAT_SCOPE` в зависимости от типа вашей учетной записи.
    *(Необязательно: Вы также можете настроить имена моделей по умолчанию и порты в файлах `.env`.)*

3.  **▶️ Запустить сервисы:**
    ```bash
    docker compose up --build -d
    ```
    *   Сервис Gemini будет доступен по адресу `http://localhost:8000`
    *   Сервис Grok будет доступен по адресу `http://localhost:8001`
    *   Сервис GigaChat будет доступен по адресу `http://localhost:8005` (или по порту, указанному в `gigachat_service/.env`)

## 📚 Документация API

*   Подробные инструкции по использованию и примеры: [docs/api_usage.ru.md](docs/api_usage.ru.md)
*   Интерактивная документация Swagger UI:
    *   Gemini: `http://localhost:8000/docs`
    *   Grok: `http://localhost:8001/docs`
    *   GigaChat: `http://localhost:8005/docs` (или по настроенному порту)

## 📜 Лицензия

Этот проект лицензирован под лицензией MIT - подробности смотрите в файле [LICENSE](LICENSE).

Copyright (c) 2025 MIREA TEAM.