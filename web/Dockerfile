FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from web directory
COPY web/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Обнови protobuf до последней версии перед генерацией proto-файлов
RUN pip install --no-cache-dir --upgrade protobuf grpcio grpcio-tools

# Copy application code from web directory
COPY web/ .

# Expose port
EXPOSE 5001

# Добавь этот ENV для корректного импорта web.*
ENV PYTHONPATH=/app:/app/web

# Копируем proto-файл в рабочую директорию контейнера
COPY ../proto/astro.proto ./astro.proto

# Создаём astro-пакет и __init__.py
RUN mkdir -p ./astro && touch ./astro/__init__.py

# Сгенерировать proto-файлы прямо в astro-пакет
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./astro.proto

# Production stage
FROM base as production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "app:app"]

# Test stage
FROM base as test
RUN pip install pytest pytest-cov pytest-asyncio
CMD ["pytest", "tests/", "-v", "--cov=.", "--cov-report=xml"]
