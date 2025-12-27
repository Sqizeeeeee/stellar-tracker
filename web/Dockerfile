FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем СВОЙ requirements.txt для веба
COPY web/requirements.txt /app/web/requirements.txt
RUN pip install --no-cache-dir -r /app/web/requirements.txt

# Копируем весь проект
COPY . .

# Генерируем proto файлы с правильной версией protobuf
RUN python -m grpc_tools.protoc \
    -I/app/proto \
    --python_out=/app/web/proto \
    --grpc_python_out=/app/web/proto \
    /app/proto/astro.proto && \
    sed -i 's/import astro_pb2/from . import astro_pb2/g' /app/web/proto/astro_pb2_grpc.py

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["python", "-u", "web/app.py"]
