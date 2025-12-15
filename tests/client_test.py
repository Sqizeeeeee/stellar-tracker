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
        object_name="ISS"
    )

    # Реальные наблюдения МКС из JPL Horizons
    # Станция: München (48.14°N, 11.58°E, 520m)
    # Период: 2024-12-15 19:00-19:10 UTC
    iss_observations = [
        ("2024-12-15T19:00:00.000Z", 263.345520, -19.178520),
        ("2024-12-15T19:05:00.000Z", 275.004090, -32.316960),
        ("2024-12-15T19:10:00.000Z", 284.815770, -45.982000),
    ]

    for obs_time, ra, dec in iss_observations:
        obs = request.observations.add()
        obs.obs_time = obs_time
        obs.ra_deg = ra
        obs.dec_deg = dec
        obs.rms_ra = 1.0  # 1 угловая секунда
        obs.rms_dec = 1.0
        obs.station = "48.14,11.58,520.0"  # München
        obs.catalog = "JPL-Horizons"

    print(f"📤 Отправляем {len(iss_observations)} реальных наблюдений МКС к Orbit Service...")
    print(f"   Источник: JPL Horizons")
    print(f"   Объект: ISS (NAIF ID -125544)")
    for i, (t, ra, dec) in enumerate(iss_observations, 1):
        print(f"   {i}. {t} - RA: {ra:9.6f}°, Dec: {dec:9.6f}°")

    try:
        response = stub.Calculate(request, timeout=10)
    except grpc.RpcError as e:
        print(f"❌ RPC Error: {e.code()} — {e.details()}")
        return

    print("\n✅ Orbit Service ответил:")
    print(f"   Request ID: {response.request_id}")
    print(f"   Success:    {response.success}")

    if response.success:
        orbit = response.orbit
        print("   Элементы орбиты:")
        print(f"     a  = {orbit.a_au:.8f} AU ({orbit.a_au * 149597870.7:.1f} km)")
        print(f"     e  = {orbit.e:.6f}")
        print(f"     i  = {orbit.i_deg:.2f}°")
        print(f"     ω  = {orbit.omega_deg:.2f}°")
        print(f"     Ω  = {orbit.big_mega_deg:.2f}°")
        print(f"     M  = {orbit.m_deg:.2f}°")
        print(f"     Epoch = {orbit.epoch}")
        
        # Проверка на реалистичность для МКС
        altitude_km = (orbit.a_au * 149597870.7) - 6371  # радиус Земли
        print(f"\n   📊 Анализ орбиты:")
        print(f"      Высота: {altitude_km:.0f} км")
        print(f"      Ожидаемая высота МКС: ~410 км")
        print(f"      Ожидаемый наклон МКС: ~51.6°")
        
        if 350 < altitude_km < 450 and orbit.e < 0.01 and 50 < orbit.i_deg < 53:
            print(f"      ✅ Орбита соответствует параметрам МКС!")
        elif 200 < altitude_km < 2000 and orbit.e < 0.2:
            print(f"      ✅ Орбита реалистична для LEO")
        elif altitude_km < 0:
            print(f"      ❌ Орбита под поверхностью Земли")
        else:
            print(f"      ⚠️  Орбита необычная")
    else:
        print(f"   ❌ Ошибка: {response.error}")


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
        object_name="ISS-Full-Test"
    )

    # Те же реальные наблюдения МКС
    observations = [
        ("2024-12-15T19:00:00.000Z", 263.345520, -19.178520),
        ("2024-12-15T19:05:00.000Z", 275.004090, -32.316960),
        ("2024-12-15T19:10:00.000Z", 284.815770, -45.982000),
    ]

    for i, (t, ra, dec) in enumerate(observations):
        obs = request.observations.add()
        obs.obs_time = t
        obs.ra_deg = ra
        obs.dec_deg = dec
        obs.rms_ra = 1.0
        obs.rms_dec = 1.0
        obs.station = "48.14,11.58,520.0"
        obs.catalog = "JPL-Horizons"
        print(f"📡 Observation {i+1}: RA={ra:9.6f}°, Dec={dec:9.6f}°, Time={t}")

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
        print(f"     Перигелий (AU):         {risk.perihelion_au:.6f}")
        print(f"     MOID Земли (AU):        {risk.moid_earth_au:.6f}")
        print(f"     Потенциальное событие:  {risk.potential_impact}")
    else:
        print(f"   ❌ Ошибка: {response.error}")


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