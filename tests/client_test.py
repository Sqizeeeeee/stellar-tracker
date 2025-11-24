# test_client.py
import grpc
import astro_pb2
import astro_pb2_grpc

def test_request():
    channel = grpc.insecure_channel('localhost:50051')  # Orchestrator
    stub = astro_pb2_grpc.OrchestratorServiceStub(channel)
    
    # Создаем тестовые наблюдения
    request = astro_pb2.ObservationsRequest()
    request.request_id = "test-123"
    request.object_name = "TestObject"
    
    # Добавляем 3 наблюдения (минимум)
    obs1 = request.observations.add()
    obs1.obs_time = "2024-01-01T00:00:00Z"
    obs1.ra_deg = 120.5
    obs1.dec_deg = 45.2
    obs1.station = "500"

    obs2 = request.observations.add()
    obs2.obs_time = "2024-01-01T00:30:00Z" 
    obs2.ra_deg = 120.6
    obs2.dec_deg = 45.3
    obs2.station = "500"

    obs3 = request.observations.add()
    obs3.obs_time = "2024-01-01T01:00:00Z"
    obs3.ra_deg = 120.7
    obs3.dec_deg = 45.4
    obs3.station = "500"
    
    response = stub.Process(request)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_request()