# Builder
FROM ubuntu:22.04 AS builder

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

# Генерируем proto для всех сервисов
RUN protoc \
      --cpp_out=orchestrator/proto \
      --grpc_out=orchestrator/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

RUN protoc \
      --cpp_out=orbit-service/proto \
      --grpc_out=orbit-service/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Собираем ВСЕ проекты из корня
WORKDIR /src
RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . --config Release

# Runtime
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем оба бинарника
COPY --from=builder /src/build/orchestrator/orchestrator /usr/local/bin/
COPY --from=builder /src/build/orbit-service/orbit_service /usr/local/bin/

EXPOSE 50051 50052
CMD ["orchestrator"]  # По умолчанию запускаем orchestrator