#include <grpcpp/grpcpp.h>
#include <grpcpp/alarm.h>
#include <thread>
#include <chrono>
#include <memory>
#include <iostream>

#include "astro.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using astro::ObservationsRequest;
using astro::OrbitResponse;
using astro::OrbitElements;
using astro::RiskResponse;
using astro::OrbitService;
using astro::CollisionService;
using astro::OrchestratorService;

// ===============================================
// Вспомогательная функция: вызов с retry (минимум 5 попыток)
// ===============================================
template<typename Stub, typename Request, typename Response>
bool CallWithRetry(
    std::unique_ptr<Stub>& stub,
    grpc::Status (Stub::*method)(grpc::ClientContext*, const Request&, Response*),
    const Request& request,
    Response* response,
    int max_attempts = 5,
    int base_delay_ms = 100)
{
    for (int attempt = 1; attempt <= max_attempts; ++attempt) {
        grpc::ClientContext context;
        // Таймаут 10 сек на каждую попытку
        context.set_deadline(std::chrono::system_clock::now() + std::chrono::seconds(10));

        grpc::Status status = (stub.get()->*method)(&context, request, response);

        if (status.ok()) {
            return true;
        }

        std::cerr << "Попытка " << attempt << " неудачна: " 
                  << status.error_code() << " - " << status.error_message() << std::endl;

        if (attempt < max_attempts) {
            int delay_ms = base_delay_ms * (1 << (attempt - 1)); // экспоненциальный backoff
            std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
        }
    }
    return false;
}

// ===============================================
// Реализация OrchestratorService
// ===============================================
class OrchestratorServiceImpl final : public OrchestratorService::Service {
public:
    explicit OrchestratorServiceImpl(
        const std::string& orbit_addr,
        const std::string& collision_addr)
    {
        orbit_stub_ = OrbitService::NewStub(
            grpc::CreateChannel(orbit_addr, grpc::InsecureChannelCredentials()));
        collision_stub_ = CollisionService::NewStub(
            grpc::CreateChannel(collision_addr, grpc::InsecureChannelCredentials()));
    }

    Status Process(ServerContext* context,
                   const ObservationsRequest* request,
                   RiskResponse* reply) override
    {
        // 1. Получаем орбиту (с 5 попытками)
        OrbitResponse orbit_resp;
        if (!CallWithRetry(orbit_stub_, &OrbitService::Stub::Calculate, *request, &orbit_resp)) {
            reply->set_success(false);
            reply->set_error("Не удалось связаться с OrbitService после 5 попыток");
            reply->set_request_id(request->request_id());
            return Status::OK;
        }

        if (!orbit_resp.success()) {
            reply->set_success(false);
            reply->set_error("OrbitService вернул ошибку: " + orbit_resp.error());
            reply->set_request_id(request->request_id());
            return Status::OK;
        }

        // 2. Оцениваем риски (с 5 попытками)
        RiskResponse risk_resp;
        if (!CallWithRetry(collision_stub_, &CollisionService::Stub::AssessRisk,
                           orbit_resp.orbit(), &risk_resp)) {
            reply->set_success(false);
            reply->set_error("Не удалось связаться с CollisionService после 5 попыток");
            reply->set_request_id(request->request_id());
            return Status::OK;
        }

        // Всё успешно — копируем результат
        *reply = risk_resp;
        return Status::OK;
    }

private:
    std::unique_ptr<OrbitService::Stub> orbit_stub_;
    std::unique_ptr<CollisionService::Stub> collision_stub_;
};