#include <iostream>
#include <chrono>
#include "../src/algorithms/least_squares_determinator.h"
#include "../src/utils/csv_loader.h"

void benchmarkNASA_Method() {
    std::cout << "=== БЕНЧМАРК NASA МЕТОДА НАИМЕНЬШИХ КВАДРАТОВ ===" << std::endl;
    
    try {
        auto observations = CsvLoader::loadObservations("../data/test_encke.csv");
        LeastSquaresDeterminator determinator;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        const int iterations = 10; // Меньше итераций, т.к. метод сложнее
        for (int i = 0; i < iterations; ++i) {
            OrbitalElements elements = determinator.determineOrbit(observations);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Время выполнения (" << iterations << " итераций): " 
                  << duration.count() << " мкс" << std::endl;
        std::cout << "Среднее время на расчёт: " 
                  << duration.count() / iterations << " мкс" << std::endl;
                  
    } catch (const std::exception& e) {
        std::cout << "❌ Ошибка: " << e.what() << std::endl;
    }
}

int main() {
    benchmarkNASA_Method();
    return 0;
}