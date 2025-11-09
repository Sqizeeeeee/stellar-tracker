#include "csv_loader.h"
#include <iostream>
#include <fstream>

std::vector<Observation> CsvLoader::loadObservations(const std::string& filename) {
    std::vector<Observation> observations;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filename);
    }
    
    std::string line;
    std::getline(file, line); // Пропускаем заголовок
    
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string token;
        Observation obs;
        
        // Читаем JD
        std::getline(ss, token, ',');
        obs.julian_date = std::stod(token);
        
        // Читаем RA
        std::getline(ss, token, ',');
        obs.right_ascension = std::stod(token);
        
        // Читаем Dec
        std::getline(ss, token, ',');
        obs.declination = std::stod(token);
        
        // Читаем object_type (если есть)
        if (std::getline(ss, token, ',')) {
            obs.object_type = token;
        } else {
            obs.object_type = ""; // Пустое значение по умолчанию
        }
        
        observations.push_back(obs);
    }
    
    return observations;
}

bool CsvLoader::fileExists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}