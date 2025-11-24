#include <grpcpp/grpcpp.h>
#include <iostream>
#include "astro.grpc.pb.h"
#include "orbit_calculator.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using astro::OrbitService;
using astro::ObservationsRequest;
using astro::OrbitResponse;

#include <grpcpp/grpcpp.h>
#include <iostream>
#include "astro.grpc.pb.h"
#include "orbit_calculator.h"  // Добавляем include

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using astro::OrbitService;
using astro::ObservationsRequest;
using astro::OrbitResponse;

class OrbitServiceImpl final : public OrbitService::Service {
    Status Calculate(ServerContext* context,
                    const ObservationsRequest* request,
                    OrbitResponse* response) override {
        
        std::cout << "OrbitService получил запрос для объекта: " 
                  << request->object_name() << std::endl;
        
        OrbitCalculator calculator;
        *response = calculator.CalculateOrbit(*request);
        
        return Status::OK;
    }
};

int main() {
    std::string server_address("0.0.0.0:50052");
    OrbitServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "OrbitService слушает на " << server_address << std::endl;
    server->Wait();

    return 0;
}