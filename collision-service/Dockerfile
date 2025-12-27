FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt
COPY collision-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем proto из корня проекта
COPY proto /app/proto

# Генерируем proto файлы с правильной версией protobuf
RUN python -m grpc_tools.protoc \
    -I/app/proto \
    --python_out=/app/proto \
    --grpc_python_out=/app/proto \
    /app/proto/astro.proto && \
    sed -i 's/import astro_pb2/from . import astro_pb2/g' /app/proto/astro_pb2_grpc.py

# Копируем код сервиса
COPY collision-service/server.py server.py

CMD ["python", "-u", "server.py"]
