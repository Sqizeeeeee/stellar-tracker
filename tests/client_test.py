#!/usr/bin/env python3
"""
Запускай: python -m pytest tests/ -v
или просто: python tests/client_test.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import grpc
import time
from web.proto import astro_pb2, astro_pb2_grpc


def test_orchestrator_is_alive():
    # Даём оркестратору пару секунд на старт (если запускаем вместе)
    time.sleep(2)

    channel = grpc.insecure_channel('localhost:50051')
    stub = astro_pb2_grpc.OrchestratorServiceStub(channel)

    request = astro_pb2.ObservationsRequest(
        request_id="test-001",
        object_name="2025 PQ77",
        observations=[]  # пока пусто, потом добавим
    )

    try:
        response = stub.Process(request, timeout=10)
        print("УСПЕХ! Оркестратор ответил:")
        print(f"   request_id: {response.request_id}")
        print(f"   success:    {response.success}")
        print(f"   error:      {response.error or 'нет'}")
        if response.success:
            print(f"   risk_level: {response.risk_level:.10f}")
            print(f"   probability: {response.collision_probability:.10f}")
        assert response.request_id == "test-001"
    except grpc.RpcError as e:
        print(f"ОШИБКА: {e.code()} — {e.details()}")
        raise


if __name__ == "__main__":
    print("Запускаем пионерский тест твоего C++ оркестратора...\n")
    test_orchestrator_is_alive()
    print("\nВсё работает! Ты — бог микросервисов 2025 года!")