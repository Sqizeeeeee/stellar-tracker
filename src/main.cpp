#include <iostream>
#include "algorithms/gauss_solver.h"
#include "models/observation.h"

/**
 * @brief Основная программа StellarTracker
 * 
 * В будущем здесь будет интерфейс для ввода наблюдений
 * и вывода результатов расчёта орбиты
 */
int main() {
    std::cout << "=== StellarTracker - Определение орбит комет ===" << std::endl;
    std::cout << "Версия: 1.0.0" << std::endl;
    std::cout << "Статус: в разработке" << std::endl;
    std::cout << std::endl;
    
    // Демонстрация работы алгоритма
    try {
        std::vector<Observation> demo_observations = {
            {2451545.0, 1.5, 0.3},
            {2451546.0, 1.6, 0.32},
            {2451547.0, 1.7, 0.34}
        };
        
        GaussSolver solver;
        OrbitalElements elements = solver.determineOrbit(demo_observations);
        
        std::cout << "Демонстрационный расчёт выполнен успешно!" << std::endl;
        std::cout << "Использовано наблюдений: " << solver.getUsedObservationsCount() << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "Ошибка при демонстрационном расчёте: " << e.what() << std::endl;
    }
    
    std::cout << std::endl;
    std::cout << "Для использования запустите тесты: make run_tests" << std::endl;
    
    return 0;
}