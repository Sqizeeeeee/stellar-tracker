# Builder
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Копируем только исходный код (БЕЗ старых proto файлов)
COPY proto/ ./proto/
COPY orchestrator/src ./orchestrator/src
COPY orchestrator/include ./orchestrator/include
COPY orchestrator/CMakeLists.txt ./orchestrator/

# Генерируем proto файлы используя системный protoc 3.12.4
RUN mkdir -p orchestrator/proto && \
    protoc --version && \
    protoc \
      --cpp_out=orchestrator/proto \
      --grpc_out=orchestrator/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto && \
    ls -la orchestrator/proto/

# Собираем orchestrator
WORKDIR /src/orchestrator
RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Runtime
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем собранный бинарник
COPY --from=builder /src/orchestrator/build/orchestrator /usr/local/bin/

EXPOSE 50051
CMD ["orchestrator"]