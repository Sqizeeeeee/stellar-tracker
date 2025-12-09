import grpc
from concurrent import futures
import time
from proto import astro_pb2, astro_pb2_grpc

class OrbitServiceServicer(astro_pb2_grpc.OrbitServiceServicer):
    def Calculate(self, request, context):
        response = astro_pb2.OrbitResponse()
        response.request_id = request.request_id

        # Заглушка орбиты
        orbit = response.orbit
        orbit.a_au = 1.2
        orbit.e = 0.05
        orbit.i_deg = 12.3
        orbit.omega_deg = 45.0
        orbit.big_mega_deg = 150.0
        orbit.m_deg = 10.0
        orbit.epoch = "2024-01-01T00:00:00Z"

        response.success = True
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    astro_pb2_grpc.add_OrbitServiceServicer_to_server(OrbitServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("OrbitService слушает на порту 50052")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
