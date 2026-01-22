FROM ubuntu:22.04 as base

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libgrpc++-dev \
    libprotobuf-dev \
    protobuf-compiler-grpc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source code
COPY . .

# Build stage
FROM base as builder

RUN mkdir -p build && cd build \
    && cmake .. \
    && make -j$(nproc)

# Production stage
FROM ubuntu:22.04 as production

RUN apt-get update && apt-get install -y \
    libgrpc++1.45 \
    libprotobuf23 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/build/orchestrator /app/orchestrator

EXPOSE 50051

CMD ["./orchestrator"]

# Test stage
FROM builder as test

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

CMD ["ctest", "--output-on-failure"]
