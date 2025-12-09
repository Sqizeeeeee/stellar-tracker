#!/usr/bin/env python3
import grpc
import time
import sys

# ---------------------------
# Безопасный импорт protobuf
# ---------------------------
try:
    import astro_pb2, astro_pb2_grpc
except ImportError:
    print("❌ Не удалось импортировать proto-модули.")
    print("   Убедись, что PYTHONPATH содержит путь к ./proto")
    sys.exit(1)

# ===========================
# Utility functions
# ===========================

def wait_for_channel(address, timeout=3):
    """Ожидает доступности gRPC канала."""
    channel = grpc.insecure_channel(address)
    try:
        grpc.channel_ready_future(channel).result(timeout=timeout)
        return True
    except grpc.FutureTimeoutError:
        return False


def log_header(text: str):
    print("\n" + "═" * 60)
    print(text)
    print("═" * 60)


# ===========================
# HEALTH CHECK
# ===========================

def check_services_health():
    """Проверка доступности всех gRPC сервисов"""
    log_header("🏥 Проверка здоровья сервисов")

    services = [
        ('Orchestrator', 'localhost:50051'),
        ('Orbit Service', 'localhost:50052'),
        ('Collision Service', 'localhost:50053')
    ]

    for name, address in services:
        ok = wait_for_channel(address)
        if ok:
            print(f"   ✅ {name:<18} {address} — доступен")
        else:
            print(f"   ❌ {name:<18} {address} — недоступен")


# ===========================
# DIRECT ORBIT-SERVICE TEST
# ===========================

def test_orbit_service_directly():
    log_header("🎯 Прямое тестирование Orbit Service")

    address = "localhost:50052"
    if not wait_for_channel(address):
        print("❌ Orbit Service недоступен")
        return

    channel = grpc.insecure_channel(address)
    stub = astro_pb2_grpc.OrbitServiceStub(channel)

    request = astro_pb2.ObservationsRequest(
        request_id=f"direct-test-{int(time.time())}",
        object_name="DirectTestObject"
    )

    # Минимальный набор наблюдений
    for i in range(3):
        obs = request.observations.add()
        obs.obs_time = f"2024-01-01T0{i}:00:00Z"
        obs.ra_deg = 120.5 + i * 0.1
        obs.dec_deg = 45.2 + i * 0.1
        obs.station = "500"

    print("📤 Отправляем запрос к Orbit Service...")

    try:
        response = stub.Calculate(request, timeout=10)
    except grpc.RpcError as e:
        print(f"❌ RPC Error: {e.code()} — {e.details()}")
        return

    print("✅ Orbit Service ответил:")
    print(f"   Request ID: {response.request_id}")
    print(f"   Success:    {response.success}")

    if response.success:
        orbit = response.orbit
        print("   Элементы орбиты:")
        print(f"     a  = {orbit.a_au}")
        print(f"     e  = {orbit.e}")
        print(f"     i  = {orbit.i_deg}°")
        print(f"     ω  = {orbit.omega_deg}°")
        print(f"     Ω  = {orbit.big_mega_deg}°")
        print(f"     M  = {orbit.m_deg}°")
        print(f"     Epoch = {orbit.epoch}")
    else:
        print(f"   Ошибка: {response.error}")


# ===========================
# FULL ORCHESTRATOR TEST
# ===========================

def test_orchestrator():
    log_header("🚀 Тестирование полного цикла через Orchestrator")

    address = "localhost:50051"
    if not wait_for_channel(address):
        print("❌ Orchestrator недоступен")
        return

    channel = grpc.insecure_channel(address)
    stub = astro_pb2_grpc.OrchestratorServiceStub(channel)

    request = astro_pb2.ObservationsRequest(
        request_id=f"test-{int(time.time())}",
        object_name="TestAsteroid"
    )

    observations = [
        ("2024-01-01T00:00:00Z", 120.5, 45.2),
        ("2024-01-01T00:30:00Z", 120.6, 45.3),
        ("2024-01-01T01:00:00Z", 120.7, 45.4),
        ("2024-01-01T01:30:00Z", 120.8, 45.5),
        ("2024-01-01T02:00:00Z", 120.9, 45.6),
    ]

    for i, (t, ra, dec) in enumerate(observations):
        obs = request.observations.add()
        obs.obs_time = t
        obs.ra_deg = ra
        obs.dec_deg = dec
        obs.station = "500"
        obs.catalog = "TestCatalog"
        print(f"📡 Observation {i+1}: RA={ra}, Dec={dec}, Time={t}")

    print(f"\n📤 Отправляем запрос в Orchestrator ({request.request_id})...")

    try:
        response = stub.Process(request, timeout=30)
    except grpc.RpcError as e:
        print(f"❌ RPC Error: {e.code()} — {e.details()}")
        return

    print("\n✅ Ответ от Orchestrator:")
    print(f"   Request ID: {response.request_id}")
    print(f"   Success:    {response.success}")

    if response.success:
        risk = response.risk
        print("   Риск столкновения:")
        print(f"     Уровень:                {risk.risk_level}")
        print(f"     MOID Земли (AU):        {risk.moid_earth_au}")
        print(f"     Потенциальное событие:  {risk.potential_impact}")
    else:
        print(f"   Ошибка: {response.error}")


# ===========================
# MAIN
# ===========================

if __name__ == "__main__":
    log_header("🧪 Комплексный тест микросервисов")

    check_services_health()

    print("\n⏳ Ожидание стабилизации сервисов...")
    time.sleep(3)

    test_orbit_service_directly()
    test_orchestrator()
