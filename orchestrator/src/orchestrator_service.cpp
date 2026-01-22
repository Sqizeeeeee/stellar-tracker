#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <optional>
#include <chrono>
#include "astro.grpc.pb.h"
#include "metrics_server.h"

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
                                     const std::optional<std::string>& orbit_addr_opt = std::nullopt,
                                     MetricsServer* metrics = nullptr)
        : collision_stub_(CollisionService::NewStub(
              grpc::CreateChannel(collision_addr, grpc::InsecureChannelCredentials()))),
          metrics_(metrics) {

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
        if (metrics_) {
            metrics_->IncrementRequests();
            metrics_->IncrementActive();
        }

        std::cout << "📡 Получен запрос: " << request->request_id() 
                  << " для объекта '" << request->object_name() << "'" << std::endl;
        std::cout << "   Наблюдений: " << request->observations_size() << std::endl;

        reply->set_request_id(request->request_id());

        std::unique_ptr<OrbitResponse> orbit_resp = std::make_unique<OrbitResponse>();

        // Если OrbitService доступен - вызываем его
        if (orbit_stub_) {
            std::cout << "   → Вызываю OrbitService..." << std::endl;
            ClientContext orbit_ctx;
            orbit_ctx.set_deadline(std::chrono::system_clock::now() + std::chrono::seconds(5));
            Status orbit_status = orbit_stub_->Calculate(&orbit_ctx, *request, orbit_resp.get());
            
            if (!orbit_status.ok()) {
                std::cout << "   ❌ OrbitService недоступен: " << orbit_status.error_message() << std::endl;
                reply->set_success(false);
                reply->set_error("OrbitService недоступен: " + orbit_status.error_message());
                if (metrics_) {
                    metrics_->IncrementFailed();
                    metrics_->DecrementActive();
                }
                return Status::OK;
            }
            
            if (!orbit_resp->success()) {
                std::cout << "   ❌ OrbitService вернул ошибку: " << orbit_resp->error() << std::endl;
                reply->set_success(false);
                reply->set_error("OrbitService ошибка: " + orbit_resp->error());
                if (metrics_) {
                    metrics_->IncrementFailed();
                    metrics_->DecrementActive();
                }
                return Status::OK;
            }
            
            std::cout << "   ✅ OrbitService вернул орбиту: a=" << orbit_resp->orbit().a_au() << " AU" << std::endl;
        } else {
            // Заглушка если OrbitService не доступен
            std::cout << "   ⚠️ OrbitService отключен, использую заглушку" << std::endl;
            orbit_resp->set_success(true);
            orbit_resp->set_request_id(request->request_id());
            astro::OrbitElements* orbit = orbit_resp->mutable_orbit();
            orbit->set_a_au(1.0);
            orbit->set_e(0.1);
            orbit->set_i_deg(5.0);
            orbit->set_epoch("2024-01-01T00:00:00Z");
        }

        // Вызываем CollisionService - результат получаем в отдельный объект
        std::cout << "   → Вызываю CollisionService..." << std::endl;
        RiskResponse collision_resp;  // ИСПРАВЛЕНО: создаем отдельный объект для ответа от CollisionService
        ClientContext collision_ctx;
        collision_ctx.set_deadline(std::chrono::system_clock::now() + std::chrono::seconds(10));
        Status collision_status = collision_stub_->AssessRisk(&collision_ctx, orbit_resp->orbit(), &collision_resp);
        
        if (!collision_status.ok()) {
            std::cout << "   ❌ CollisionService ошибка: " << collision_status.error_message() << std::endl;
            reply->set_success(false);
            reply->set_error("CollisionService ошибка: " + collision_status.error_message());
            if (metrics_) {
                metrics_->IncrementFailed();
                metrics_->DecrementActive();
            }
            return Status::OK;
        }

        std::cout << "   ✅ CollisionService вернул риск: " << collision_resp.risk().risk_level() << std::endl;
        
        // ИСПРАВЛЕНО: Теперь собираем финальный ответ из обоих результатов
        reply->set_success(true);
        reply->mutable_orbit()->CopyFrom(orbit_resp->orbit());  // Копируем орбиту
        reply->mutable_risk()->CopyFrom(collision_resp.risk());  // Копируем риск
        
        std::cout << "   → Финальный ответ: orbit.a=" << reply->orbit().a_au() 
                  << " AU, risk=" << reply->risk().risk_level() << std::endl;
        std::cout << "✓ Запрос обработан успешно!" << std::endl;
        
        if (metrics_) {
            metrics_->IncrementSuccess();
            metrics_->DecrementActive();
        }
        return Status::OK;
    }

private:
    std::unique_ptr<OrbitService::Stub> orbit_stub_;
    std::unique_ptr<CollisionService::Stub> collision_stub_;
    MetricsServer* metrics_;
};