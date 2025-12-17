import grpc
from concurrent import futures
import time
import random
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Импортируем сгенерированные файлы
from web.proto import astro_pb2, astro_pb2_grpc

# Prometheus метрики
COLLISION_CHECKS = Counter('collision_checks_total', 'Total collision checks performed')
COLLISION_DURATION = Histogram('collision_check_duration_seconds', 'Time spent on collision check')
HIGH_RISK_DETECTIONS = Counter('high_risk_detections_total', 'Total high risk detections')
ACTIVE_REQUESTS = Gauge('collision_service_active_requests', 'Number of active collision check requests')


class CollisionService(astro_pb2_grpc.CollisionServiceServicer):
    def CheckCollision(self, request, context):
        ACTIVE_REQUESTS.inc()
        COLLISION_CHECKS.inc()
        
        with COLLISION_DURATION.time():
            # Имитация тяжёлых расчётов
            time.sleep(0.3 + random.random() * 0.4)

            risk = random.uniform(0.0, 1.0)
            prob = 0.0
            if risk > 0.8:
                prob = random.uniform(0.0001, 0.3)
                HIGH_RISK_DETECTIONS.inc()
            elif risk > 0.5:
                prob = random.uniform(0.000001, 0.0001)

        ACTIVE_REQUESTS.dec()
        
        return astro_pb2.RiskResponse(
            request_id=request.request_id,
            success=True,
            risk_level=risk,
            collision_probability=prob,
            closest_approach_km=random.uniform(50, 500000),
            timestamp=int(time.time())
        )


def main():
    # Запускаем HTTP сервер для Prometheus метрик на порту 8001
    start_http_server(8001)
    print("Prometheus metrics доступны на http://localhost:8001/metrics")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    astro_pb2_grpc.add_CollisionServiceServicer_to_server(CollisionService(), server)
    server.add_insecure_port('[::]:50053')
    print("CollisionService запущен на порту 50053")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()