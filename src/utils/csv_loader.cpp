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
    
    // Пропускаем заголовок
    std::getline(file, line);
    
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        Observation obs;
        
        // Читаем JD
        std::getline(ss, cell, ',');
        obs.julian_date = std::stod(cell);
        
        // Читаем RA
        std::getline(ss, cell, ',');
        obs.right_ascension = std::stod(cell);
        
        // Читаем Dec
        std::getline(ss, cell, ',');
        obs.declination = std::stod(cell);
        
        if (obs.isValid()) {
            observations.push_back(obs);
        }
    }
    
    return observations;
}

bool CsvLoader::fileExists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}