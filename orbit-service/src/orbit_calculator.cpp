#include "orbit_calculator.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <memory>

astro::OrbitResponse OrbitCalculator::CalculateOrbit(const astro::ObservationsRequest& request) {
    astro::OrbitResponse response;
    response.set_request_id(request.request_id());
    
    std::cout << "[OrbitCalculator] Starting calculation for request: " 
              << request.request_id() << std::endl;
    
    // 1. Валидация
    std::cout << "[OrbitCalculator] Validating " << request.observations_size() 
              << " observations..." << std::endl;
    if (!ValidateRequest(request)) {
        response.set_success(false);
        response.set_error("Invalid observations data");
        std::cerr << "[OrbitCalculator] Validation failed" << std::endl;
        return response;
    }
    
    // 2. Подготовка файла
    std::cout << "[OrbitCalculator] Preparing observations file..." << std::endl;
    std::string observations_file = PrepareObservationsFile(request);
    if (observations_file.empty()) {
        response.set_success(false);
        response.set_error("Failed to prepare observations file");
        return response;
    }
    
    // 3. Запуск find_orb
    std::string findorb_output;
    if (!RunFindOrb(observations_file, findorb_output)) {
        response.set_success(false);
        response.set_error("Failed to run find_orb");
        return response;
    }
    
    // 4. Парсинг результата
    astro::OrbitElements elements = ParseFindOrbOutput(findorb_output);
    response.mutable_orbit()->CopyFrom(elements);
    response.set_success(true);
    
    return response;
}


bool OrbitCalculator::ValidateRequest(const astro::ObservationsRequest& request) {
    // Проверка количества наблюдений
    if (request.observations_size() < 3) {
        std::cerr << "Need at least 3 observations, got: " 
                  << request.observations_size() << std::endl;
        return false;
    }

    // Проверка каждого наблюдения
    for (int i = 0; i < request.observations_size(); ++i) {
        const auto& obs = request.observations(i);
        
        // Проверка RA
        if (obs.ra_deg() < 0 || obs.ra_deg() >= 360) {
            std::cerr << "Observation " << i << ": Invalid RA " << obs.ra_deg() 
                      << " (must be 0-360)" << std::endl;
            return false;
        }
        
        // Проверка Dec
        if (obs.dec_deg() < -90 || obs.dec_deg() > 90) {
            std::cerr << "Observation " << i << ": Invalid Dec " << obs.dec_deg()
                      << " (must be -90 to 90)" << std::endl;
            return false;
        }
        
        // Проверка времени
        if (obs.obs_time().empty()) {
            std::cerr << "Observation " << i << ": Empty observation time" << std::endl;
            return false;
        }
    }

    return true;
}



std::string OrbitCalculator::PrepareObservationsFile(const astro::ObservationsRequest& request) {
    std::string filename = "/tmp/observations_" + request.request_id() + ".txt";
    std::ofstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Cannot create observations file: " << filename << std::endl;
        return "";
    }

    // Формат MPC: станция RA Dec время
    for (const auto& obs : request.observations()) {
        file << obs.station() << " " 
             << obs.ra_deg() << " " 
             << obs.dec_deg() << " " 
             << obs.obs_time() << "\n";
    }
    
    file.close();
    return filename;
}


bool OrbitCalculator::RunFindOrb(const std::string& observations_file, std::string& output) {
    std::string command = "find_orb " + observations_file + " 2>&1";
    
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        std::cerr << "Failed to run find_orb" << std::endl;
        return false;
    }

    char buffer[128];
    while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        output += buffer;
    }

    return !output.empty();
}

astro::OrbitElements OrbitCalculator::ParseFindOrbOutput(const std::string& findorb_output) {
    astro::OrbitElements elements;
    
    // TODO: Реальный парсинг вывода find_orb
    // Сейчас заглушка для тестирования
    elements.set_a_au(2.5);
    elements.set_e(0.1);
    elements.set_i_deg(5.0);
    elements.set_omega_deg(180.0);
    elements.set_big_mega_deg(90.0);
    elements.set_m_deg(45.0);
    elements.set_epoch("2024-01-01T00:00:00Z");
    
    return elements;
}