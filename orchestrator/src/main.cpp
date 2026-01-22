#include <grpcpp/grpcpp.h>
#include <iostream>
#include "metrics_server.h"
#include "orchestrator_service.cpp"
#include "astro.grpc.pb.h"

using astro::OrchestratorService;

int main(int argc, char** argv) {
    if (argc > 1 && std::string(argv[1]) == "--test") {
        std::cout << "Test mode" << std::endl;
        return 0;
    }
    
    std::cout << "Orchestrator starting..." << std::endl;

    // CollisionService — обязателен
    const std::string collision_addr = 
        std::getenv("COLLISION_SERVICE_ADDR") ? std::getenv("COLLISION_SERVICE_ADDR") : "localhost:50053";

    // OrbitService — опционален (если переменная не задана — будет заглушка)
    std::optional<std::string> orbit_addr_opt = std::nullopt;
    if (std::getenv("ORBIT_SERVICE_ADDR") && std::strlen(std::getenv("ORBIT_SERVICE_ADDR")) > 0) {
        orbit_addr_opt = std::getenv("ORBIT_SERVICE_ADDR");
    }

    std::cout << "Orchestrator стартует...\n";

    // Создаем metrics server
    MetricsServer metrics;
    metrics.Start(8000);

    OrchestratorServiceImpl service(collision_addr, orbit_addr_opt, &metrics);

    grpc::ServerBuilder builder;
    builder.AddListeningPort("0.0.0.0:50051", grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "Orchestrator слушает на 0.0.0.0:50051\n";
    std::cout << "Готов к приёму запросов!\n\n";
    std::cout << std::endl << std::flush;

    server->Wait();
    return 0;
}