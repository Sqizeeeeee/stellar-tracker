# Builder
FROM ubuntu:22.04 AS builder

# Устанавливаем зависимости только для orchestrator
RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev libgrpc++1 \
    libgtest-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

# Генерируем proto ТОЛЬКО для orchestrator
RUN protoc \
      --cpp_out=orchestrator/proto \
      --grpc_out=orchestrator/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Собираем ТОЛЬКО orchestrator из корня
WORKDIR /src
RUN mkdir -p build && cd build && \
    cmake .. -DBUILD_ORBIT_SERVICE=OFF -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . --target orchestrator --config Release

# Runtime
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем ТОЛЬКО orchestrator бинарник
COPY --from=builder /src/build/orchestrator/orchestrator /usr/local/bin/

EXPOSE 50051
CMD ["orchestrator"]