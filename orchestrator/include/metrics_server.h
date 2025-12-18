#pragma once

#include <string>
#include <sstream>
#include <atomic>
#include <chrono>
#include <thread>
#include <memory>

// Простой HTTP сервер для метрик Prometheus
class MetricsServer {
public:
    MetricsServer() : 
        requests_total_(0),
        requests_success_(0),
        requests_failed_(0),
        active_requests_(0) {}

    void IncrementRequests() { ++requests_total_; }
    void IncrementSuccess() { ++requests_success_; }
    void IncrementFailed() { ++requests_failed_; }
    void IncrementActive() { ++active_requests_; }
    void DecrementActive() { --active_requests_; }

    std::string GetMetrics() const {
        std::stringstream ss;
        
        // Process metrics
        ss << "# HELP process_requests_total Total number of requests processed\n";
        ss << "# TYPE process_requests_total counter\n";
        ss << "process_requests_total{service=\"orchestrator\"} " << requests_total_ << "\n\n";
        
        ss << "# HELP process_requests_success Total number of successful requests\n";
        ss << "# TYPE process_requests_success counter\n";
        ss << "process_requests_success{service=\"orchestrator\"} " << requests_success_ << "\n\n";
        
        ss << "# HELP process_requests_failed Total number of failed requests\n";
        ss << "# TYPE process_requests_failed counter\n";
        ss << "process_requests_failed{service=\"orchestrator\"} " << requests_failed_ << "\n\n";
        
        ss << "# HELP orchestrator_active_requests Number of currently active requests\n";
        ss << "# TYPE orchestrator_active_requests gauge\n";
        ss << "orchestrator_active_requests " << active_requests_.load() << "\n\n";
        
        return ss.str();
    }

    // Запуск простого HTTP сервера на указанном порту
    void Start(int port);

private:
    std::atomic<uint64_t> requests_total_;
    std::atomic<uint64_t> requests_success_;
    std::atomic<uint64_t> requests_failed_;
    std::atomic<int32_t> active_requests_;
};
