#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <cstdlib>

#include "astro.grpc.pb.h"

class OrchestratorServiceImpl final : public astro::OrchestratorService::Service {
    // (весь код из orchestrator_service.cpp переносим сюда пока)
    // Позже вынесем в .h/.cpp, но сейчас для быстрого запуска — всё в одном файле
public:
    explicit OrchestratorServiceImpl(const std::string& orbit_addr, const std::string& collision_addr) {
        orbit_stub_ = astro::OrbitService::NewStub(
            grpc::CreateChannel(orbit_addr, grpc::InsecureChannelCredentials()));
        collision_stub_ = astro::CollisionService::NewStub(
            grpc::CreateChannel(collision_addr, grpc::InsecureChannelCredentials()));
    }

    grpc::Status Process(grpc::ServerContext* context,
                         const astro::ObservationsRequest* request,
                         astro::RiskResponse* reply) override {
        reply->set_request_id(request->request_id());
        reply->set_success(false);
        reply->set_error("OrbitService и CollisionService пока не запущены — это заглушка");
        return grpc::Status::OK;
    }

private:
    std::unique_ptr<astro::OrbitService::Stub> orbit_stub_;
    std::unique_ptr<astro::CollisionService::Stub> collision_stub_;
};

int main() {
    std::string orbit_addr = std::getenv("ORBIT_SERVICE_ADDR") ? std::getenv("ORBIT_SERVICE_ADDR") : "localhost:50052";
    std::string collision_addr = std::getenv("COLLISION_SERVICE_ADDR") ? std::getenv("COLLISION_SERVICE_ADDR") : "localhost:50053";

    OrchestratorServiceImpl service(orbit_addr, collision_addr);

    grpc::ServerBuilder builder;
    builder.AddListeningPort("0.0.0.0:50051", grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "Orchestrator запущен и слушает на 0.0.0.0:50051\n";
    server->Wait();
}