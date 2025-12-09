# Базовый образ с Python 3.11
FROM python:3.11-slim

# Устанавливаем зависимости
RUN pip install --no-cache-dir grpcio grpcio-tools protobuf numpy scipy astropy jax jaxlib

# Создаём рабочую папку
WORKDIR /app

# Копируем proto файлы в контейнер
COPY proto/ ./proto/

# Генерируем Python gRPC файлы прямо в папку proto/
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    ./proto/astro.proto

# Копируем основной сервис
COPY orbit-service/orbit_service.py .

# Убедимся, что папка proto — пакет Python
RUN touch proto/__init__.py

# Открываем порт gRPC
EXPOSE 50052

# Запуск сервиса
CMD ["python", "orbit_service.py"]
