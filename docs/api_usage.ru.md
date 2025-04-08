# Документация API - Сервисы OCR и Чата (Gemini & Grok)

Этот документ описывает, как интегрировать и использовать API, предоставляемые сервисами OCR Gemini и OCR Grok Vision.

## Общая информация

### Базовые URL (По умолчанию при запуске через Docker Compose)

*   **OCR Gemini Service:** `http://localhost:8000`
*   **OCR Grok Vision Service:** `http://localhost:8001`

*(Примечание: Эти порты могут изменяться в зависимости от вашей конфигурации развертывания)*

### Аутентификация

Оба сервиса используют аутентификацию на основе ключа API через HTTP-заголовок.

*   **Имя заголовка:** `X-API-Key`
*   **Значение:** Соответствующий ключ API (Google API Key для Gemini, XAI API Key для Grok).

Если ключ API настроен в файле `.env` сервиса на стороне сервера, вам не нужно отправлять этот заголовок. Используйте этот заголовок, если вы хотите переопределить или предоставить ключ API для каждого запроса.

---

## 1. OCR Gemini Service

**Базовый URL:** `http://localhost:8000`

### 1.1. Извлечение текста из изображения (OCR)

*   **Конечная точка (Endpoint):** `POST /ocr/extract-text`
*   **Описание:** Загрузите файл изображения для извлечения текста с помощью модели Gemini Vision.
*   **Заголовки (Headers):**
    *   `X-API-Key`: (Необязательно) Google API Key.
*   **Тело запроса (Request Body):** `multipart/form-data`
    *   `file`: (Обязательно) Файл изображения для обработки (Разрешенные типы: `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`).
    *   `prompt`: (Необязательно) Текстовая строка для управления моделью (например, "Извлечь только адрес"). По умолчанию извлекается весь текст.
    *   `model_name`: (Необязательно) Имя конкретной модели Gemini Vision для использования (например, `gemini-2.0-flash-exp-image-generation`). По умолчанию используется значение из конфигурации (`GEMINI_VISION_MODEL_NAME`).
*   **Ответ (Успех - 200 OK):** `application/json`
    ```json
    {
      "filename": "имя_файла_изображения.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Извлеченное текстовое содержимое...",
      "model_used": "gemini-2.0-flash-exp-image-generation" // Пример использованной модели
    }
    ```
*   **Ответ (Ошибка):** `application/json` (Примеры: 400, 422, 500, 503)
    ```json
    {
      "detail": "Подробное описание ошибки..."
    }
    ```
*   **Пример (curl):**
    ```bash
    curl -X POST "http://localhost:8000/ocr/extract-text?prompt=Extract%20only%20the%20invoice%20number&model_name=gemini-2.0-flash-exp-image-generation" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -F "file=@/путь/к/вашему/изображению.png"
    ```

### 1.2. Текстовый чат (Chat)

*   **Конечная точка (Endpoint):** `POST /chat/`
*   **Описание:** Отправьте сообщение и историю чата, чтобы получить ответ от модели Gemini Text.
*   **Заголовки (Headers):**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Необязательно) Google API Key.
*   **Тело запроса (Request Body):** `application/json`
    ```json
    {
      "message": "Новое сообщение пользователя",
      "history": [
        {"role": "user", "content": "Предыдущее сообщение пользователя"},
        {"role": "assistant", "content": "Предыдущий ответ модели"}
        // ... другие реплики
      ],
      "model_name": "gemini-2.0-flash" // Необязательно: переопределить модель по умолчанию (напр., использовать flash для чата)
    }
    ```
    *   `message`: (Обязательно) Последнее сообщение от пользователя.
    *   `history`: (Необязательно) Список предыдущих сообщений. `role` должен быть `"user"` или `"assistant"`.
    *   `model_name`: (Необязательно) Имя конкретной модели Gemini Text для использования (например, `gemini-2.0-flash`). По умолчанию используется значение из конфигурации (`GEMINI_TEXT_MODEL_NAME`).
*   **Ответ (Успех - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Ответ от модели Gemini...",
      "model_used": "gemini-2.0-flash" // Пример использованной модели
    }
    ```
*   **Ответ (Ошибка):** `application/json` (Примеры: 400, 500, 503)
    ```json
    {
      "detail": "Подробное описание ошибки..."
    }
    ```
*   **Пример (curl):**
    ```bash
    curl -X POST "http://localhost:8000/chat/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_GOOGLE_API_KEY" \
         -d '{
               "message": "Какая столица Франции?",
               "history": [
                 {"role": "user", "content": "Привет"},
                 {"role": "assistant", "content": "Привет!"}
               ],
               "model_name": "gemini-2.0-flash"
             }'
    ```

---

## 2. OCR Grok Vision Service

**Базовый URL:** `http://localhost:8001`

### 2.1. Извлечение текста из изображения (OCR)

*   **Конечная точка (Endpoint):** `POST /ocr/extract-text`
*   **Описание:** Загрузите файл изображения для извлечения текста с помощью модели Grok Vision.
*   **Заголовки (Headers):**
    *   `X-API-Key`: (Необязательно) XAI API Key.
*   **Тело запроса (Request Body):** `multipart/form-data`
    *   `file`: (Обязательно) Файл изображения для обработки (Разрешенные типы: `image/jpeg`, `image/png`).
    *   `prompt`: (Необязательно) Текстовая строка для управления моделью. По умолчанию извлекается весь текст.
    *   `model_name`: (Необязательно) Имя конкретной модели Grok Vision для использования (например, `grok-2-vision-1212`). По умолчанию используется значение из конфигурации (`GROK_VISION_DEFAULT_MODEL`).
*   **Ответ (Успех - 200 OK):** `application/json`
    ```json
    {
      "filename": "имя_файла_изображения.jpg",
      "content_type": "image/jpeg",
      "extracted_text": "Извлеченное текстовое содержимое...",
      "model_used": "grok-2-vision-1212" // Пример использованной модели
    }
    ```
*   **Ответ (Ошибка):** `application/json` (Примеры: 400, 415, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Подробное описание ошибки..."
    }
    ```
*   **Пример (curl):**
    ```bash
    curl -X POST "http://localhost:8001/ocr/extract-text?model_name=grok-2-vision-1212" \
         -H "X-API-Key: YOUR_XAI_API_KEY" \
         -F "file=@/путь/к/вашему/изображению.jpg"
    ```

### 2.2. Текстовый чат (Chat)

*   **Конечная точка (Endpoint):** `POST /chat/`
*   **Описание:** Отправьте сообщение и историю чата, чтобы получить ответ от модели Grok Text.
*   **Заголовки (Headers):**
    *   `Content-Type`: `application/json`
    *   `X-API-Key`: (Необязательно) XAI API Key.
*   **Тело запроса (Request Body):** `application/json`
    ```json
    {
      "message": "Новое сообщение пользователя",
      "history": [
        {"role": "user", "content": "Предыдущее сообщение пользователя"},
        {"role": "assistant", "content": "Предыдущий ответ модели"}
        // ... другие реплики
      ],
      "model_name": "grok-2-1212" // Необязательно: переопределить модель по умолчанию (напр., использовать grok-2 для чата)
    }
    ```
    *   `message`: (Обязательно) Последнее сообщение от пользователя.
    *   `history`: (Необязательно) Список предыдущих сообщений. `role` должен быть `"user"` или `"assistant"`.
    *   `model_name`: (Необязательно) Имя конкретной модели Grok Text для использования (например, `grok-2-1212`). По умолчанию используется значение из конфигурации (`GROK_TEXT_DEFAULT_MODEL`).
*   **Ответ (Успех - 200 OK):** `application/json`
    ```json
    {
      "response_text": "Ответ от модели Grok...",
      "model_used": "grok-2-1212" // Пример использованной модели
    }
    ```
*   **Ответ (Ошибка):** `application/json` (Примеры: 400, 429, 500, 502, 503, 504)
    ```json
    {
      "detail": "Подробное описание ошибки..."
    }
    ```
*   **Пример (curl):**
    ```bash
    curl -X POST "http://localhost:8001/chat/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: YOUR_XAI_API_KEY" \
         -d '{
               "message": "Объясните концепцию zero-shot learning.",
               "history": [],
               "model_name": "grok-2-1212"
             }'
    ```

---

## 3. Проверка работоспособности (Health Check)

Оба сервиса предоставляют конечную точку для проверки их рабочего состояния.

*   **Конечная точка (Endpoint):** `GET /health/`
*   **Описание:** Возвращает текущий статус сервиса.
*   **Ответ (Успех - 200 OK):** `application/json`
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
*   **Пример (curl):**
    ```bash
    curl -X GET http://localhost:8000/health/
    curl -X GET http://localhost:8001/health/