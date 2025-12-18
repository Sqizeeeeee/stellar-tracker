#include "metrics_server.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

void MetricsServer::Start(int port) {
    std::thread([this, port]() {
        int server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd < 0) {
            std::cerr << "Failed to create metrics socket\n";
            return;
        }

        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        struct sockaddr_in address;
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(port);

        if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
            std::cerr << "Failed to bind metrics server to port " << port << "\n";
            close(server_fd);
            return;
        }

        if (listen(server_fd, 10) < 0) {
            std::cerr << "Failed to listen on metrics port\n";
            close(server_fd);
            return;
        }

        std::cout << "📊 Metrics server listening on http://0.0.0.0:" << port << "/metrics\n";

        while (true) {
            int client_fd = accept(server_fd, nullptr, nullptr);
            if (client_fd < 0) continue;

            char buffer[1024] = {0};
            read(client_fd, buffer, 1024);

            // Проверяем, что это GET /metrics
            if (std::strstr(buffer, "GET /metrics") != nullptr) {
                std::string metrics = GetMetrics();
                std::string response = 
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain; version=0.0.4\r\n"
                    "Content-Length: " + std::to_string(metrics.length()) + "\r\n"
                    "\r\n" + metrics;
                
                write(client_fd, response.c_str(), response.length());
            } else {
                // Для всех остальных путей возвращаем 404
                std::string response = 
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "\r\n";
                write(client_fd, response.c_str(), response.length());
            }

            close(client_fd);
        }

        close(server_fd);
    }).detach();
}
