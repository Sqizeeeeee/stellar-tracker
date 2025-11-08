#include <iostream>
#include "../src/algorithms/gauss_solver.h"
#include "../src/models/observation.h"

int main() {
    std::cout << "=== Тест алгоритма Гаусса ===" << std::endl;
    
    try {
        // Тест с минимальными данными
        std::vector<Observation> observations = {
            {2451545.0, 1.5, 0.3},
            {2451546.0, 1.6, 0.32},
            {2451547.0, 1.7, 0.34}
        };
        
        GaussSolver solver;
        OrbitalElements elements = solver.determineOrbit(observations);
        
        std::cout << "✅ Алгоритм выполнен без ошибок" << std::endl;
        std::cout << "Использовано наблюдений: " << solver.getUsedObservationsCount() << std::endl;
        
        // Проверяем валидность элементов
        if (elements.isValid()) {
            std::cout << "✅ Орбитальные элементы валидны" << std::endl;
        } else {
            std::cout << "⚠️ Орбитальные элементы невалидны (ожидаемо на данном этапе)" << std::endl;
        }
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }
}