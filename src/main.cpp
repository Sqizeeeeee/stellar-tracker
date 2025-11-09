#include <iostream>
#include "algorithms/least_squares_determinator.h"
#include "utils/csv_loader.h"

int main() {
    std::cout << "StellarTracker - Определение орбит комет" << std::endl;
    
    try {
        // Загружаем данные
        auto observations = CsvLoader::loadObservations("data/test_encke.csv");
        std::cout << "Загружено наблюдений: " << observations.size() << std::endl;
        
        // Определяем орбиту
        LeastSquaresDeterminator determinator;
        OrbitalElements orbit = determinator.determineOrbit(observations);
        
        if (orbit.isValid()) {
            std::cout << "\nОрбита определена успешно!" << std::endl;
            std::cout << "Эксцентриситет: " << orbit.eccentricity << std::endl;
            std::cout << "Большая полуось: " << orbit.semi_major_axis << " а.е." << std::endl;
        } else {
            std::cout << "\nНе удалось определить орбиту" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}