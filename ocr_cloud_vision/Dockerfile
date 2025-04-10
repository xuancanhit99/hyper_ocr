# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during build
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any are needed - keep gcc/curl from reference for now, might be needed for some pip installs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /app/app
COPY main.py .

# Expose the port the app runs on (matching the reference and default config)
EXPOSE 6363

# Define the command to run the application
# Use the standard uvicorn command format
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6363"]