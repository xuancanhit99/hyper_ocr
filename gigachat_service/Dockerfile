# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed (e.g., for libraries like Pillow or Tesseract)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*
# GigaChat client likely doesn't need extra system deps beyond Python libs

# Install pip dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
# Use the ARG and ENV pattern to make the port configurable at build time if needed,
# but default to the one in settings (though uvicorn command below uses settings directly)
ARG APP_PORT=8005
EXPOSE ${APP_PORT}

# Define the command to run the application
# Use the port from the environment variable loaded by config.py
# Note: We run main.py which then uses uvicorn programmatically.
# Alternatively, run uvicorn directly:
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
# Running main.py allows the `if __name__ == "__main__":` block to control execution,
# which might be slightly better if startup logic exists outside uvicorn.run()
CMD ["python", "main.py"]