#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <optional>
#include <chrono>
#include "astro.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using astro::ObservationsRequest;
using astro::OrbitResponse;
using astro::RiskResponse;
using astro::OrchestratorService;
using astro::OrbitService;
using astro::CollisionService;

class OrchestratorServiceImpl final : public OrchestratorService::Service {
public:
    explicit OrchestratorServiceImpl(const std::string& collision_addr,
                                     const std::optional<std::string>& orbit_addr_opt = std::nullopt)
        : collision_stub_(CollisionService::NewStub(
              grpc::CreateChannel(collision_addr, grpc::InsecureChannelCredentials()))) {

        if (orbit_addr_opt.has_value()) {
            orbit_stub_ = OrbitService::NewStub(
                grpc::CreateChannel(orbit_addr_opt.value(), grpc::InsecureChannelCredentials()));
            std::cout << "  → OrbitService подключён: " << orbit_addr_opt.value() << "\n";
        } else {
            std::cout << "  → OrbitService отключён (заглушка)\n";
        }
        std::cout << "  → CollisionService: " << collision_addr << "\n";
    }

    Status Process(ServerContext* context,
                   const ObservationsRequest* request,
                   RiskResponse* reply) override {
        reply->set_request_id(request->request_id());

        // Пока OrbitService нет — сразу переходим к Collision (или возвращаем заглушку)
        std::unique_ptr<OrbitResponse> orbit_resp = std::make_unique<OrbitResponse>();
        if (!orbit_stub_) {
            reply->set_success(false);
            reply->set_error("OrbitService временно недоступен — сервис ещё не реализован");
            return Status::OK;
        }

        // Если вдруг потом появится — раскомментишь
        /*
        ClientContext orbit_ctx;
        orbit_ctx.set_deadline(std::chrono::system_clock::now() + std::chrono::seconds(5));
        Status orbit_status = orbit_stub_->Calculate(&orbit_ctx, *request, orbit_resp.get());
        if (!orbit_status.ok()) {
            reply->set_success(false);
            reply->set_error("OrbitService недоступен: " + orbit_status.error_message());
            return Status::OK;
        }
        */

        ClientContext collision_ctx;
        collision_ctx.set_deadline(std::chrono::system_clock::now() + std::chrono::seconds(10));
        Status collision_status = collision_stub_->AssessRisk(&collision_ctx, orbit_resp->orbit(), reply);
        if (!collision_status.ok()) {
            reply->set_success(false);
            reply->set_error("CollisionService ошибка: " + collision_status.error_message());
            return Status::OK;
        }

        reply->set_success(true);
        return Status::OK;
    }

private:
    std::unique_ptr<OrbitService::Stub> orbit_stub_;
    std::unique_ptr<CollisionService::Stub> collision_stub_;
};