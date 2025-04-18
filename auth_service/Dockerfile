# Sử dụng Python 3.9 làm base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8800

# Chạy setup Alembic config và migrations khi container khởi động
CMD ["sh", "-c", "python setup_alembic_config.py && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8800"]