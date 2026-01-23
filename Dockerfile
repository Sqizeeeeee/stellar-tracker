# Builder
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libprotobuf-dev \
    libgrpc-dev libgrpc++-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Копируем весь код сразу (включая уже сгенерированные proto файлы)
COPY . .

# Проверяем что proto файлы есть
RUN ls -la orchestrator/proto/ || echo "Proto directory not found!"

# Собираем orchestrator - proto файлы уже есть в репозитории
WORKDIR /src/orchestrator
RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make VERBOSE=1

# Runtime
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем собранный бинарник
COPY --from=builder /src/orchestrator/build/orchestrator /usr/local/bin/

EXPOSE 50051
CMD ["orchestrator"]