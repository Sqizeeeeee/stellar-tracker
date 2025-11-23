FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

RUN mkdir -p orbit-service/proto && \
    protoc \
      --cpp_out=orbit-service/proto \
      --grpc_out=orbit-service/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

WORKDIR /src/orbit-service
RUN mkdir -p build && cd build && \
    cmake .. && \
    cmake --build .

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/orbit-service/build/orbit_service /usr/local/bin/

EXPOSE 50052
CMD ["/usr/local/bin/orbit_service"]