#include <iostream>
#include <chrono>
#include "../src/algorithms/gauss_solver.h"
#include "../src/models/observation.h"

int main() {
    std::cout << "=== Бенчмарк производительности ===" << std::endl;
    
    try {
        std::vector<Observation> observations = {
            {2446470.5, 1.234, 0.567},
            {2446471.5, 1.235, 0.568},
            {2446472.5, 1.236, 0.569}
        };
        
        GaussSolver solver;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        const int iterations = 1000;
        for (int i = 0; i < iterations; ++i) {
            OrbitalElements elements = solver.determineOrbit(observations);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Время выполнения (" << iterations << " итераций): " 
                  << duration.count() << " мкс" << std::endl;
        std::cout << "Среднее время на расчёт: " 
                  << duration.count() / iterations << " мкс" << std::endl;
                  
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }
}