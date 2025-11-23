#!/usr/bin/env python3
"""
Тест оркестратора — полностью соответствует текущему astro.proto
Запуск: python tests/client_test.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent))

import grpc
from web.proto import astro_pb2, astro_pb2_grpc


def test_orchestrator_is_alive():
    print("Подключаемся к оркестратору на localhost:50051...\n")
    time.sleep(1)

    channel = grpc.insecure_channel("localhost:50051")
    stub = astro_pb2_grpc.OrchestratorServiceStub(channel)

    # Генерируем ISO 8601 время (UTC)
    now = datetime.now(timezone.utc)
    past1 = now.replace(hour=now.hour - 2)
    past2 = now.replace(hour=now.hour - 1)

    request = astro_pb2.ObservationsRequest(
        request_id="test-001",
        object_name="2025 PQ77",
        observations=[
            astro_pb2.Observation(
                obs_time=past1.isoformat().replace("+00:00", "Z"),
                ra_deg=185.123456,
                dec_deg=+12.345678,
                rms_ra=0.12,
                rms_dec=0.15,
                station="T14",
                catalog="Gaia DR3"
            ),
            astro_pb2.Observation(
                obs_time=past2.isoformat().replace("+00:00", "Z"),
                ra_deg=185.234567,
                dec_deg=+12.456789,
                rms_ra=0.10,
                rms_dec=0.13,
                station="T14",
                catalog="Gaia DR3"
            ),
            astro_pb2.Observation(
                obs_time=now.isoformat().replace("+00:00", "Z"),
                ra_deg=185.345678,
                dec_deg=+12.567890,
                rms_ra=0.08,
                rms_dec=0.09,
                station="T14",
                catalog="Gaia DR3"
            ),
        ]
    )

    try:
        response = stub.Process(request, timeout=15.0)

        print("УСПЕХ! Оркестратор ответил:\n")
        print(f"   request_id           : {response.request_id}")
        print(f"   success              : {response.success}")

        if not response.success:
            print(f"   error                : {response.error}")
            print("\n   Связь есть! Осталось реализовать orbit-service")
        else:
            risk = response.risk
            print(f"   risk_level           : {risk.risk_level}")
            print(f"   potential_impact     : {risk.potential_impact}")
            print(f"   MOID (Earth)         : {risk.moid_earth_au:.6f} AU")
            print(f"   Perihelion           : {risk.perihelion_au:.6f} AU")
            print("\n   ПОЛНЫЙ УСПЕХ! ВСЁ РАБОТАЕТ НА 100%!")

        assert response.request_id == "test-001"

    except grpc.RpcError as e:
        print(f"ОШИБКА СОЕДИНЕНИЯ: {e.code()} — {e.details()}")
        print("Убедись, что docker-compose up запущен")
        raise


if __name__ == "__main__":
    print("Запускаем тест твоего C++ оркестратора...\n")
    test_orchestrator_is_alive()