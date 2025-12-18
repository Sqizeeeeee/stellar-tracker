FROM python:3.11-slim
WORKDIR /app

# Копируем proto файлы сервиса
COPY collision-service/proto ./proto
COPY collision-service/server.py server.py

# Устанавливаем зависимости
RUN pip install --no-cache-dir grpcio grpcio-tools prometheus-client

# Открываем порты: 50053 для gRPC, 8003 для Prometheus метрик
EXPOSE 50053 8003

# Запускаем с отключенной буферизацией вывода
CMD ["python", "-u", "server.py"]