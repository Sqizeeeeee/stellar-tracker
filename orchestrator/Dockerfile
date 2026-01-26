FROM python:3.10-slim as base

WORKDIR /app

# Установим системные зависимости (если нужны)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости приложения
COPY orchestrator/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Обновим protobuf и grpcio-tools до последних версий
RUN pip install --no-cache-dir --upgrade protobuf grpcio grpcio-tools

# Копируем исходники приложения
COPY orchestrator/ .

# Копируем proto-файл из корня проекта
COPY ../proto/astro.proto ./astro.proto

# Создаём proto-пакет и __init__.py
RUN mkdir -p ./proto && touch ./proto/__init__.py

# Сгенерировать proto-файлы прямо в proto-пакет
RUN python -m grpc_tools.protoc -I. --python_out=./proto --grpc_python_out=./proto ./astro.proto

# Expose ports
EXPOSE 50051
EXPOSE 8000

# Добавляем PYTHONPATH для корректного импорта
ENV PYTHONPATH=/app:/app/proto

# Production stage
FROM base as production

WORKDIR /app

# Явно выводим содержимое директории для отладки (можно удалить после диагностики)
RUN ls -l /app

CMD ["python", "server.py"]
