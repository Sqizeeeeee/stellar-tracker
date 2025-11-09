#include <iostream>
#include <vector>
#include "../src/algorithms/least_squares_determinator.h"
#include "../src/utils/csv_loader.h"

void testCometHalley() {
    std::cout << "=== ТЕСТ КОМЕТЫ ГАЛЛЕЯ (1P/Halley) ===" << std::endl;
    
    try {
        auto observations = CsvLoader::loadObservations("../data/test_halley.csv");
        std::cout << "Загружено наблюдений: " << observations.size() << std::endl;
        
        LeastSquaresDeterminator determinator;
        OrbitalElements orbit = determinator.determineOrbit(observations);
        
        std::cout << "\n=== РЕЗУЛЬТАТЫ ===" << std::endl;
        if (orbit.isValid()) {
            std::cout << "✓ Орбита успешно определена!" << std::endl;
            std::cout << "Эксцентриситет (e): " << orbit.eccentricity << " (ожидается ~0.967)" << std::endl;
            std::cout << "Большая полуось (a): " << orbit.semi_major_axis << " а.е. (ожидается ~17.8 а.е.)" << std::endl;
            std::cout << "Наклонение (i): " << orbit.inclination * 180.0 / M_PI << "° (ожидается ~162°)" << std::endl;
        } else {
            std::cout << "✗ Не удалось определить валидную орбиту" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "ОШИБКА: " << e.what() << std::endl;
    }
}

int main() {
    testCometHalley();
    return 0;
}