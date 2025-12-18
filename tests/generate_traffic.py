#!/usr/bin/env python3
"""
Генератор трафика для тестирования метрик мониторинга
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grpc
import time
import random
from web.proto import astro_pb2, astro_pb2_grpc

def generate_collision_checks(n=10):
    """Генерирует N запросов проверки столкновений"""
    channel = grpc.insecure_channel('localhost:50053')
    stub = astro_pb2_grpc.CollisionServiceStub(channel)
    
    print(f"🚀 Отправляю {n} запросов к Collision Service...")
    
    for i in range(n):
        # Создаем орбитальные элементы для проверки столкновений
        orbit = astro_pb2.OrbitElements(
            a_au=random.uniform(0.8, 1.5),
            e=random.uniform(0.0, 0.3),
            i_deg=random.uniform(0, 30),
            omega_deg=random.uniform(0, 360),
            big_mega_deg=random.uniform(0, 360),
            M_deg=random.uniform(0, 360),
            epoch="2024-12-18T12:00:00Z"
        )
        
        try:
            response = stub.AssessRisk(orbit, timeout=5.0)
            if response.success and response.risk:
                status = "⚠️ HIGH" if response.risk.risk_level == "high" else \
                        "⚡ MOD" if response.risk.risk_level == "moderate" else "✅ LOW"
                print(f"  [{i+1}/{n}] {status} Risk: {response.risk.risk_level}, "
                      f"MOID: {response.risk.moid_earth_au:.4f} AU")
            else:
                print(f"  [{i+1}/{n}] ⚠️  Error: {response.error}")
        except grpc.RpcError as e:
            print(f"  [{i+1}/{n}] ❌ Error: {e.code()}")
        
        time.sleep(0.5)  # Небольшая пауза между запросами
    
    print("✅ Готово! Проверьте метрики в Grafana")
    channel.close()

def generate_orbit_determinations(n=5):
    """Генерирует N запросов определения орбиты"""
    channel = grpc.insecure_channel('localhost:50052')
    stub = astro_pb2_grpc.OrbitServiceStub(channel)
    
    print(f"\n🛰️  Отправляю {n} запросов к Orbit Service...")
    
    for i in range(n):
        # Создаем 3 наблюдения для определения орбиты
        observations = [
            astro_pb2.Observation(
                obs_time=f"2024-12-18T{10+j:02d}:30:45.123Z",
                ra_deg=random.uniform(0, 360),
                dec_deg=random.uniform(-90, 90),
                station="500",
                catalog="Gaia2"
            )
            for j in range(3)
        ]
        
        request = astro_pb2.ObservationsRequest(
            request_id=f"orbit-test-{i}",
            object_name=f"TEST-{random.randint(1000, 9999)}",
            observations=observations
        )
        
        try:
            response = stub.Calculate(request, timeout=10.0)
            if response.success and response.orbit:
                print(f"  [{i+1}/{n}] ✅ Орбита: a={response.orbit.a_au:.3f} AU, "
                      f"e={response.orbit.e:.4f}, i={response.orbit.i_deg:.1f}°")
            else:
                print(f"  [{i+1}/{n}] ⚠️  Ошибка: {response.error}")
        except grpc.RpcError as e:
            print(f"  [{i+1}/{n}] ❌ Error: {e.code()}")
        
        time.sleep(1.0)
    
    print("✅ Готово! Проверьте метрики в Grafana")
    channel.close()

def generate_orchestrator_requests(n=10):
    """Генерирует N запросов к Orchestrator (полный пайплайн)"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = astro_pb2_grpc.OrchestratorServiceStub(channel)
    
    print(f"\n🎯 Отправляю {n} запросов к Orchestrator (полный пайплайн)...")
    
    for i in range(n):
        # Создаем 3 наблюдения
        observations = [
            astro_pb2.Observation(
                obs_time=f"2024-12-18T{10+j:02d}:30:45.123Z",
                ra_deg=random.uniform(0, 360),
                dec_deg=random.uniform(-90, 90),
                station="500",
                catalog="Gaia2"
            )
            for j in range(3)
        ]
        
        request = astro_pb2.ObservationsRequest(
            request_id=f"full-pipeline-{i}",
            object_name=f"NEO-{random.randint(1000, 9999)}",
            observations=observations
        )
        
        try:
            response = stub.Process(request, timeout=15.0)
            if response.success and response.risk:
                status_icon = "🔴" if response.risk.potential_impact else \
                             "🟡" if response.risk.risk_level == "moderate" else "🟢"
                print(f"  [{i+1}/{n}] {status_icon} {response.risk.risk_level.upper()}: "
                      f"MOID={response.risk.moid_earth_au:.4f} AU, "
                      f"Impact={response.risk.potential_impact}")
            else:
                print(f"  [{i+1}/{n}] ⚠️  Ошибка: {response.error}")
        except grpc.RpcError as e:
            print(f"  [{i+1}/{n}] ❌ Error: {e.code()}")
        
        time.sleep(0.8)
    
    print("✅ Готово! Проверьте метрики в Grafana")
    channel.close()

if __name__ == "__main__":
    print("=" * 60)
    print("ГЕНЕРАТОР ТРАФИКА ДЛЯ STELLARTRACKER")
    print("=" * 60)
    
    # Генерируем запросы к orchestrator (полный пайплайн)
    generate_orchestrator_requests(15)
    
    # Генерируем запросы к orbit service
    generate_orbit_determinations(15)
    
    print("\n" + "=" * 60)
    print("🎉 Все запросы отправлены!")
    print("📊 Откройте Grafana: http://localhost:3000")
    print("=" * 60)
