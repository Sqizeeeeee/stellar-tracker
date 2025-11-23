# Builder
FROM ubuntu:22.04 AS builder

# Устанавливаем всё нужное, включая protobuf-compiler-grpc для grpc_cpp_plugin
RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

# Генерируем proto — grpc_cpp_plugin теперь точно в /usr/bin
RUN mkdir -p orchestrator/src/proto && \
    protoc \
      --cpp_out=orchestrator/src/proto \
      --grpc_out=orchestrator/src/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Собираем
WORKDIR /src/orchestrator
RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . --config Release

# Runtime
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/orchestrator/build/orchestrator /usr/local/bin/orchestrator

EXPOSE 50051
CMD ["orchestrator"]