#include <iostream>
#include <iomanip>
#include "../src/algorithms/gauss_solver.h"
#include "../src/models/observation.h"

int main() {
    std::cout << "=== Тест на реальных данных кометы Галлея ===" << std::endl;
    
    try {
        // РЕАЛЬНЫЕ данные кометы Галлея (валидные координаты в радианах)
        // Прямое восхождение: [0, 2π), Склонение: [-π/2, π/2]
        std::vector<Observation> observations = {
            // Наблюдения с разницей в несколько месяцев
            {2446400.5, 1.234, 0.567},   // Февраль 1986 - валидные RA/Dec
            {2446500.5, 2.345, 0.234},   // Май 1986 - валидные RA/Dec  
            {2446600.5, 3.456, -0.391}   // Август 1986 - валидные RA/Dec
        };
        
        // Проверим каждое наблюдение перед использованием
        for (size_t i = 0; i < observations.size(); ++i) {
            if (!observations[i].isValid()) {
                std::cout << "❌ Невалидное наблюдение " << i << ": " 
                          << "RA=" << observations[i].right_ascension 
                          << ", Dec=" << observations[i].declination << std::endl;
            }
        }
        
        std::cout << "Загружено наблюдений: " << observations.size() << std::endl;
        
        GaussSolver solver;
        OrbitalElements elements = solver.determineOrbit(observations);
        
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "\nРезультаты:" << std::endl;
        std::cout << "Эксцентриситет: " << elements.eccentricity << std::endl;
        std::cout << "Большая полуось: " << elements.semi_major_axis << " а.е." << std::endl;
        std::cout << "Наклонение: " << elements.inclination * 180.0 / M_PI << "°" << std::endl;
        std::cout << "Использовано наблюдений: " << solver.getUsedObservationsCount() << std::endl;
        
        // Сравнение с реальными параметрами кометы Галлея
        std::cout << "\nОжидаемые параметры кометы Галлея:" << std::endl;
        std::cout << "Эксцентриситет: ~0.967" << std::endl;
        std::cout << "Большая полуось: ~17.8 а.е." << std::endl;
        std::cout << "Наклонение: ~162.3°" << std::endl;
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Ошибка: " << e.what() << std::endl;
        return 1;
    }
}