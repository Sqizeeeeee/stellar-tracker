FROM python:3.11-slim-bullseye

WORKDIR /app

# Установка Java и системных зависимостей
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Загрузка данных Orekit
RUN wget -O /tmp/orekit-data.zip \
    https://gitlab.orekit.org/orekit/orekit-data/-/archive/main/orekit-data-main.zip && \
    unzip /tmp/orekit-data.zip -d /tmp && \
    mkdir -p /app/orekit-data && \
    mv /tmp/orekit-data-main/* /app/orekit-data/ && \
    rm -rf /tmp/orekit-data*

# Копируем СВОЙ requirements.txt для orbit_service
COPY orbit_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Копируем proto файлы и генерируем код
COPY proto/ /app/proto/
RUN python -m grpc_tools.protoc \
    -I/app/proto \
    --python_out=/app/proto \
    --grpc_python_out=/app/proto \
    /app/proto/astro.proto

# Исправляем импорты в сгенерированных файлах
RUN sed -i 's/import astro_pb2/from . import astro_pb2/g' /app/proto/astro_pb2_grpc.py

# Копируем код сервиса
COPY orbit-service/orbit_service.py /app/

ENV OREKIT_DATA=/app/orekit-data
ENV PYTHONPATH=/app
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

CMD ["python", "orbit_service.py"]
