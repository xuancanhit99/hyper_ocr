# ✨ Набор Микросервисов Hyper OCR (OCR, Чат, Аутентификация, API Gateway и др.)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Этот проект предоставляет набор микросервисов, включающий:
*   **Сервисы OCR:** Использующие Google Gemini, XAI Grok, Google Cloud Vision и Tesseract.
*   **Сервис Чата:** Использующий Sber GigaChat.
*   **Вспомогательный Сервис:** Разделение счета на основе результатов OCR.
*   **Сервис Аутентификации:** Управление аутентификацией и авторизацией пользователей.
*   **API Gateway:** Kong для управления, защиты и маршрутизации API-запросов.
*   **Мониторинг:** Prometheus, Grafana и Uptime Kuma для наблюдения за состоянием и производительностью сервисов.

## ✅ Требования

*   [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
*   [Git](https://git-scm.com/downloads)

## 🚀 Быстрый старт

1.  **Клонировать репозиторий:**
    ```bash
    git clone https://github.com/xuancanhit99/hyper_ocr.git
    cd hyper_ocr
    ```

2.  **🔑 Настроить ключи API и Окружение:**
    *   Скопируйте примеры файлов окружения для сервисов, которые вы собираетесь использовать:
        ```bash
        # Основные сервисы
        cp auth_service/.env.example auth_service/.env
        cp ocr_gemini_service/.env.example ocr_gemini_service/.env
        cp ocr_grok_vision_service/.env.example ocr_grok_vision_service/.env
        cp ocr_cloud_vision_service/.env.example ocr_cloud_vision_service/.env
        # cp ocr_pytesseract_service/.env.example ocr_pytesseract_service/.env # .env.example не найден, проверьте требования сервиса
        cp gigachat_service/.env.example gigachat_service/.env
        # cp split_bill_service/.env.example split_bill_service/.env       # .env.example не найден, проверьте требования сервиса

        # Инфраструктура (Необязательно: проверьте настройки по умолчанию в compose.yaml)
        # Конфигурации Kong, Konga, Prometheus, Grafana, Uptime Kuma в основном находятся в compose.yaml или специальных файлах конфигурации (например, monitoring/prometheus.yml)
        ```
    *   **Отредактируйте файлы `.env`** и добавьте необходимые ключи API, учетные данные или пользовательские настройки:
        *   `auth_service/.env`: Настройте подключение к базе данных, секреты и т.д.
        *   `ocr_gemini_service/.env`: Добавьте `GOOGLE_API_KEY`.
        *   `ocr_grok_vision_service/.env`: Добавьте `XAI_API_KEY`.
        *   `ocr_cloud_vision_service/.env`: Настройте учетные данные Google Cloud (например, путь `GOOGLE_APPLICATION_CREDENTIALS` при монтировании).
        *   `gigachat_service/.env`: Добавьте `GIGACHAT_AUTH_KEY` и при необходимости измените `GIGACHAT_SCOPE`, `GIGACHAT_SERVICE_PORT`.
    *(Примечание: Для сервисов без `.env.example` проверьте их соответствующие каталоги или документацию на предмет обязательных переменных окружения.)*

3.  **▶️ Запустить сервисы:**
    ```bash
    docker compose up --build -d
    ```
    *   Сервисы будут запущены. Доступ к ним осуществляется через Kong API Gateway (рекомендуется) или напрямую через их открытые порты.

## 📚 Документация API и Доступ к Сервисам

*   **API Gateway (Kong):** `http://localhost:7000` (Прокси), `http://localhost:7001` (Admin API)
*   **Интерфейс управления Gateway (Konga):** `http://localhost:7337`
*   **Мониторинг:**
    *   Prometheus: `http://localhost:9090`
    *   Grafana: `http://localhost:3000` (Логин по умолчанию: admin/admin - ИЗМЕНИТЕ ЭТО)
    *   Uptime Kuma: `http://localhost:3001`
*   **Прямой доступ к Сервисам и Swagger UI (если доступно):**
    *   Сервис Аутентификации: `http://localhost:8800` (Docs: `http://localhost:8800/docs` или `/api/docs` - проверьте путь)
    *   Gemini OCR: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
    *   Grok Vision OCR: `http://localhost:8001` (Docs: `http://localhost:8001/docs`)
    *   Cloud Vision OCR: `http://localhost:8002` (Docs: `http://localhost:8002/docs`)
    *   Pytesseract OCR: `http://localhost:8003` (Docs: `http://localhost:8003/docs`)
    *   Разделение счета: `http://localhost:8004` (Docs: `http://localhost:8004/docs`)
    *   GigaChat: `http://localhost:8005` (или настроенный порт) (Docs: `http://localhost:8005/docs`)

*   **Подробное использование API:** Смотрите [docs/api_usage.ru.md](docs/api_usage.ru.md) для примеров (требуется обновление для новых сервисов).

## 🔧 Конфигурация и Управление

*   **API Gateway (Kong):** Настройте маршруты, сервисы, плагины, потребителей и т.д. через Admin API (`:7001`) или интерфейс Konga (`:7337`).
*   **Мониторинг:** Настройте цели Prometheus в `monitoring/prometheus.yml`. Создавайте дашборды в Grafana. Настраивайте мониторы в Uptime Kuma.

## 📜 Лицензия

Этот проект лицензирован под лицензией MIT - подробности смотрите в файле [LICENSE](LICENSE).

Copyright (c) 2025 MIREA TEAM.