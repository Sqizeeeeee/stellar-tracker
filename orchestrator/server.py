import grpc
from concurrent import futures
import time
import os
import logging

from proto import astro_pb2, astro_pb2_grpc
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import sys

# Логирование в файл logs/app.log
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# Гарантируем, что файл существует (создаём пустой, если его нет)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "a", encoding="utf-8"):
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("orchestrator")

print("=== [orchestrator] server.py loaded ===", flush=True)
logger.info("server.py loaded")

ORBIT_SERVICE_ADDR = os.getenv("ORBIT_SERVICE_ADDR", "orbit-service:50052")
COLLISION_SERVICE_ADDR = os.getenv("COLLISION_SERVICE_ADDR", "collision-service:50053")

PROCESS_REQUESTS_TOTAL = Counter(
    "process_requests_total", "Total Process requests"
)
PROCESS_REQUESTS_SUCCESS = Counter(
    "process_requests_success_total", "Successful Process requests"
)
PROCESS_REQUESTS_ERROR = Counter(
    "process_requests_error_total", "Errored Process requests"
)
PROCESS_REQUEST_DURATION = Histogram(
    "process_request_duration_seconds", "Process request duration (seconds)"
)
ACTIVE_REQUESTS = Gauge("orchestrator_active_requests", "Active gRPC requests in Orchestrator")


class OrchestratorService(astro_pb2_grpc.OrchestratorServiceServicer):
    def __init__(self):
        print("=== [orchestrator] OrchestratorService instance created ===", flush=True)
        logger.info("OrchestratorService instance created")
        super().__init__()

    def Process(self, request, context):
        print("=== [orchestrator] Process called ===", flush=True)
        logger.info("Process called")
        PROCESS_REQUESTS_TOTAL.inc()
        start = time.time()
        try:
            # 1. Запрос к Orbit Service
            with grpc.insecure_channel(ORBIT_SERVICE_ADDR) as orbit_channel:
                orbit_stub = astro_pb2_grpc.OrbitServiceStub(orbit_channel)
                orbit_req = astro_pb2.ObservationsRequest(
                    request_id=request.request_id,
                    object_name=request.object_name,
                    observations=request.observations
                )
                orbit_resp = orbit_stub.Calculate(orbit_req)
                logger.info("Request to Orbit Service sent")

            # 2. Запрос к Collision Service (если орбита рассчитана)
            if orbit_resp.success and orbit_resp.orbit:
                logger.info("Orbit calculated successfully, sending to Collision Service")
                with grpc.insecure_channel(COLLISION_SERVICE_ADDR) as coll_channel:
                    coll_stub = astro_pb2_grpc.CollisionServiceStub(coll_channel)
                    coll_req = orbit_resp.orbit
                    coll_resp = coll_stub.AssessRisk(coll_req)
            else:
                logger.warning("Orbit calculation failed or orbit missing")
                coll_resp = None

            # 3. Формируем RiskResponse (по proto)
            resp = astro_pb2.RiskResponse(
                risk=coll_resp.risk if (coll_resp and coll_resp.success) else None,
                request_id=orbit_resp.request_id,
                success=orbit_resp.success and (coll_resp is None or coll_resp.success),
                error=orbit_resp.error or (coll_resp.error if coll_resp else ""),
                orbit=orbit_resp.orbit if orbit_resp.success else None
            )
            if resp.success:
                PROCESS_REQUESTS_SUCCESS.inc()
            else:
                PROCESS_REQUESTS_ERROR.inc()
            logger.info(f"Process finished, success={resp.success}")
            return resp
        except Exception as e:
            PROCESS_REQUESTS_ERROR.inc()
            print(f"=== [orchestrator] Exception in Process: {e} ===", flush=True)
            logger.exception(f"Exception in Process: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return astro_pb2.RiskResponse(
                success=False,
                error=str(e),
                request_id=getattr(request, "request_id", "")
            )
        finally:
            PROCESS_REQUEST_DURATION.observe(time.time() - start)
            logger.info("Process duration observed")


def serve():
    print("=== [orchestrator] Starting Orchestrator gRPC server... ===", file=sys.stderr, flush=True)
    logger.info("Starting Orchestrator gRPC server...")
    # Запускаем Prometheus endpoint на 0.0.0.0:8000 (важно для docker!)
    start_http_server(8000, addr="0.0.0.0")
    print("=== [orchestrator] Prometheus metrics available at 0.0.0.0:8000/metrics ===", file=sys.stderr, flush=True)
    logger.info("Prometheus metrics available at :8000/metrics")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    astro_pb2_grpc.add_OrchestratorServiceServicer_to_server(OrchestratorService(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 Orchestrator started at 0.0.0.0:50051", file=sys.stderr, flush=True)
    logger.info("Orchestrator started at 0.0.0.0:50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
