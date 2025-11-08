#include <iostream>
#include "../src/algorithms/gauss_solver.h"
#include "../src/models/observation.h"

int main() {
    std::cout << "=== Тест базовой функциональности ===" << std::endl;
    
    try {
        // Создаём тестовые наблюдения
        std::vector<Observation> test_observations = {
            {2451545.0, 1.5, 0.3},  // JD, RA, Dec
            {2451546.0, 1.6, 0.32},
            {2451547.0, 1.7, 0.34}
        };
        
        // Создаём решатель
        GaussSolver solver(3);
        
        // Пытаемся определить орбиту
        OrbitalElements elements = solver.determineOrbit(test_observations);
        
        std::cout << "Орбитальные элементы:" << std::endl;
        std::cout << "Эксцентриситет: " << elements.eccentricity << std::endl;
        std::cout << "Большая полуось: " << elements.semi_major_axis << " а.е." << std::endl;
        std::cout << "Использовано наблюдений: " << solver.getUsedObservationsCount() << std::endl;
        
        std::cout << "✅ Тест пройден успешно!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }
}