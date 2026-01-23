# Builder
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Копируем proto файлы
COPY proto/ ./proto/

# Генерируем proto для orchestrator
RUN mkdir -p orchestrator/proto && \
    protoc \
      --cpp_out=orchestrator/proto \
      --grpc_out=orchestrator/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Копируем orchestrator код
COPY orchestrator/ ./orchestrator/

# Собираем orchestrator из его директории
WORKDIR /src/orchestrator
RUN mkdir -p build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DProtobuf_PROTOC_EXECUTABLE=/usr/bin/protoc \
      -DgRPC_CPP_PLUGIN_EXECUTABLE=/usr/bin/grpc_cpp_plugin && \
    make -j$(nproc)

# Runtime
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1.45 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем собранный бинарник
COPY --from=builder /src/orchestrator/build/orchestrator /usr/local/bin/

EXPOSE 50051
CMD ["orchestrator"]