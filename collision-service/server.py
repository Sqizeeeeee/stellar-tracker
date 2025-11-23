import grpc
from concurrent import futures
import time
import random

# Импортируем сгенерированные файлы
from web.proto import astro_pb2, astro_pb2_grpc


class CollisionService(astro_pb2_grpc.CollisionServiceServicer):
    def CheckCollision(self, request, context):
        # Имитация тяжёлых расчётов
        time.sleep(0.3 + random.random() * 0.4)

        risk = random.uniform(0.0, 1.0)
        prob = 0.0
        if risk > 0.8:
            prob = random.uniform(0.0001, 0.3)
        elif risk > 0.5:
            prob = random.uniform(0.000001, 0.0001)

        return astro_pb2.RiskResponse(
            request_id=request.request_id,
            success=True,
            risk_level=risk,
            collision_probability=prob,
            closest_approach_km=random.uniform(50, 500000),
            timestamp=int(time.time())
        )


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    astro_pb2_grpc.add_CollisionServiceServicer_to_server(CollisionService(), server)
    server.add_insecure_port('[::]:50053')
    print("CollisionService запущен на порту 50053")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()