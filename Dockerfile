# Builder
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Копируем весь код сразу
COPY . .

# Генерируем proto для orchestrator используя системный protoc
RUN mkdir -p orchestrator/proto && \
    protoc --version && \
    protoc \
      --cpp_out=orchestrator/proto \
      --grpc_out=orchestrator/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Собираем orchestrator из его директории
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