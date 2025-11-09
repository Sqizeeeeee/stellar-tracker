#ifndef INITIAL_ORBIT_ESTIMATOR_H
#define INITIAL_ORBIT_ESTIMATOR_H

#include "../models/observation.h"
#include "../models/orbital_elements.h"
#include <vector>

/**
 * @brief Класс для точного вычисления начального приближения орбиты
 * 
 * Использует геометрические и кинематические методы для оценки
 * орбитальных элементов по наблюдениям
 */
class InitialOrbitEstimator {
public:
    /**
     * @brief Вычисляет начальное приближение орбиты по наблюдениям
     * @param observations Вектор наблюдений
     * @return Начальные орбитальные элементы
     */
    static OrbitalElements estimateFromObservations(const std::vector<Observation>& observations);
    
private:
    /**
     * @brief Оценивает большую полуось по третьему закону Кеплера
     */
    static double estimateSemiMajorAxis(const std::vector<Observation>& observations);
    
    /**
     * @brief Оценивает эксцентриситет по кинематике движения
     */
    static double estimateEccentricity(const std::vector<Observation>& observations);
    
    /**
     * @brief Оценивает наклонение по геометрии наблюдений
     */
    static double estimateInclination(const std::vector<Observation>& observations);
    
    /**
     * @brief Оценивает угловые элементы (Ω, ω)
     */
    static std::pair<double, double> estimateAngles(const std::vector<Observation>& observations);
    
    /**
     * @brief Оценивает время перицентра
     */
    static double estimateTimePerihelion(const std::vector<Observation>& observations);
};

#endif // INITIAL_ORBIT_ESTIMATOR_H