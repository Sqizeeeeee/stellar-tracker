"""
gRPC client для подключения к сервисам StellarTracker
"""
import grpc
import astro_pb2_grpc
from config import get_config

config = get_config()


class GRPCClient:
    """gRPC клиент для взаимодействия с сервисами"""

    def __init__(self):
        print(f"[web] Orchestrator address: {config.orchestrator_address}")
        self.orchestrator_channel = grpc.insecure_channel(config.orchestrator_address)
        self.orbit_channel = grpc.insecure_channel(config.orbit_service_address)
        self.collision_channel = grpc.insecure_channel(config.collision_service_address)

        self.orchestrator_stub = astro_pb2_grpc.OrchestratorServiceStub(self.orchestrator_channel)
        self.orbit_stub = astro_pb2_grpc.OrbitServiceStub(self.orbit_channel)
        self.collision_stub = astro_pb2_grpc.CollisionServiceStub(self.collision_channel)

    def check_health(self, service_name):
        """Проверка здоровья сервиса"""
        try:
            if service_name == 'orchestrator':
                channel = grpc.insecure_channel(config.orchestrator_address)
            elif service_name == 'orbit_service':
                channel = grpc.insecure_channel(config.orbit_service_address)
            elif service_name == 'collision_service':
                channel = grpc.insecure_channel(config.collision_service_address)
            else:
                return 'unknown'

            grpc.channel_ready_future(channel).result(timeout=1)
            channel.close()
            return 'healthy'
        except Exception:
            return 'unhealthy'

    def call_orchestrator_process(self, request_msg):
        print("[web] Calling OrchestratorService.Process...")
        return self.orchestrator_stub.Process(request_msg, timeout=30.0)

    def close(self):
        """Закрытие всех каналов"""
        self.orchestrator_channel.close()
        self.orbit_channel.close()
        self.collision_channel.close()


# Глобальный экземпляр клиента
grpc_client = GRPCClient()
