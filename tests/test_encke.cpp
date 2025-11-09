#include <iostream>
#include <vector>
#include "../src/algorithms/least_squares_determinator.h"
#include "../src/utils/csv_loader.h"
#include "../src/models/observation.h"

void testCometEncke() {
    std::cout << "=== ТЕСТ КОМЕТЫ ЭНКЕ (2P/Encke) ===" << std::endl;
    std::cout << "Сравнение с известными параметрами орбиты:" << std::endl;
    std::cout << "Ожидаемые значения: e=0.847, a=2.22 а.е., i=11.78°" << std::endl << std::endl;
    
    try {
        // Загружаем данные кометы Энке
        std::vector<Observation> observations = CsvLoader::loadObservations("../data/test_encke.csv");
        
        std::cout << "Загружено наблюдений: " << observations.size() << std::endl;
        
        // Выводим первые 3 наблюдения для проверки
        for (size_t i = 0; i < std::min(observations.size(), size_t(3)); ++i) {
            std::cout << "Наблюдение " << i+1 << ": JD=" << observations[i].julian_date 
                      << ", RA=" << observations[i].right_ascension 
                      << ", Dec=" << observations[i].declination;
            if (!observations[i].isValid()) {
                std::cout << " ⚠️ НЕВАЛИДНО!";
            }
            std::cout << std::endl;
        }
        if (observations.size() > 3) {
            std::cout << "... и еще " << observations.size() - 3 << " наблюдений" << std::endl;
        }
        
        if (observations.empty()) {
            std::cout << "ОШИБКА: Не удалось загрузить наблюдения!" << std::endl;
            return;
        }
        
        // Создаем определитель орбиты
        LeastSquaresDeterminator determinator;
        
        // Вычисляем орбиту
        std::cout << "\nЗапуск метода наименьших квадратов..." << std::endl;
        OrbitalElements orbit = determinator.determineOrbit(observations);
        
        // Выводим результаты с сравнением
        std::cout << "\n=== РЕЗУЛЬТАТЫ ДЛЯ КОМЕТЫ ЭНКЕ ===" << std::endl;
        if (orbit.isValid()) {
            std::cout << "✓ Орбита успешно определена!" << std::endl;
            std::cout << "Эксцентриситет (e): " << orbit.eccentricity << " (ожидается ~0.847)" << std::endl;
            std::cout << "Большая полуось (a): " << orbit.semi_major_axis << " а.е. (ожидается ~2.22 а.е.)" << std::endl;
            std::cout << "Наклонение (i): " << orbit.inclination * 180.0 / M_PI << "° (ожидается ~11.78°)" << std::endl;
            std::cout << "Долгота восх. узла (Ω): " << orbit.longitude_ascending * 180.0 / M_PI << "°" << std::endl;
            std::cout << "Аргумент перицентра (ω): " << orbit.argument_perihelion * 180.0 / M_PI << "°" << std::endl;
            std::cout << "Время перицентра (T): JD " << orbit.time_perihelion << std::endl;
            
            // Простая оценка точности
            std::cout << "\n=== ОЦЕНКА ТОЧНОСТИ ===" << std::endl;
            double e_error = std::abs(orbit.eccentricity - 0.847) / 0.847 * 100;
            double a_error = std::abs(orbit.semi_major_axis - 2.22) / 2.22 * 100;
            double i_error = std::abs(orbit.inclination * 180/M_PI - 11.78) / 11.78 * 100;
            
            std::cout << "Погрешность эксцентриситета: " << e_error << "%" << std::endl;
            std::cout << "Погрешность большой полуоси: " << a_error << "%" << std::endl;
            std::cout << "Погрешность наклонения: " << i_error << "%" << std::endl;
            
        } else {
            std::cout << "✗ Не удалось определить валидную орбиту" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "ОШИБКА: " << e.what() << std::endl;
    }
}

int main() {
    testCometEncke();
    return 0;
}