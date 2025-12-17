FROM python:3.11-slim-bullseye

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Скачиваем и распаковываем данные Orekit
RUN wget -O /tmp/orekit-data.zip \
    https://gitlab.orekit.org/orekit/orekit-data/-/archive/main/orekit-data-main.zip && \
    unzip /tmp/orekit-data.zip -d /tmp/ && \
    mv /tmp/orekit-data-main /app/orekit-data && \
    rm /tmp/orekit-data.zip

# Устанавливаем переменные окружения для Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV OREKIT_DATA=/app/orekit-data
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Устанавливаем Python пакеты
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    orekit-jpype \
    numpy \
    scipy \
    astropy \
    pandas \
    grpcio \
    grpcio-tools \
    protobuf \
    prometheus-client

# Копируем proto файлы и генерируем Python код
COPY proto/ /app/proto/
RUN python -m grpc_tools.protoc \
    -I/app/proto \
    --python_out=/app/proto \
    --grpc_python_out=/app/proto \
    /app/proto/astro.proto

# Исправляем импорты в сгенерированных файлах
RUN sed -i 's/import astro_pb2/from . import astro_pb2/g' /app/proto/astro_pb2_grpc.py

# Копируем сервис
COPY orbit-service/orbit_service.py /app/

# Устанавливаем переменные окружения
ENV OREKIT_DATA_PATH=/app/orekit-data
ENV PYTHONPATH=/app

EXPOSE 50052

CMD ["python", "orbit_service.py"]