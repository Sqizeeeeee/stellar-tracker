#!/bin/bash
set -e

# Путь к protoc (обычно уже есть в системе или в Docker)
PROTOC="protoc"

# Папки для генерации
CPP_OUT="../orchestrator/src/proto"
PYTHON_OUT="../web/proto"           # для Flask
PYTHON_COLLISION="../collision-service/app/proto"

mkdir -p "$CPP_OUT" "$PYTHON_OUT" "$PYTHON_COLLISION"

echo "Генерируем C++ код..."
$PROTOC --cpp_out="$CPP_OUT" \
        --grpc_out="$CPP_OUT" \
        --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` \
        astro.proto

echo "Генерируем Python код..."
$PROTOC --python_out="$PYTHON_OUT" \
        --grpc_out="$PYTHON_OUT" \
        --plugin=protoc-gen-grpc_python=`which grpc_python_plugin` \
        astro.proto

# Копируем Python-код и в collision-service (чтобы не дублировать)
cp "$PYTHON_OUT"/*_pb2*.py "$PYTHON_COLLISION/"

echo "Готово! Код сгенерирован в:"
echo "  C++ → $CPP_OUT"
echo "  Python → $PYTHON_OUT и $PYTHON_COLLISION"