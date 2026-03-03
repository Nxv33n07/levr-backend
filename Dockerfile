FROM python:3.11-slim

# Set environment variables
# 1. Prevent Python from writing .pyc files
# 2. Ensure stdout/stderr are unbuffered for real-time logging in cloud consoles
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install build dependencies if needed (none for now, keeping it light)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# (.dockerignore ensures we don't copy venv, pycache, or secrets)
COPY app ./app

# Set up a non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser $APP_HOME
USER appuser

EXPOSE 8000

# Use shell form to support dynamic $PORT from cloud providers (Railway, Render, Fly.io)
# Default to 8000 for local development
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]