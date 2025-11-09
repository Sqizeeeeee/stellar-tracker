#pragma once
#include "../models/observation.h"
#include "../models/orbital_elements.h"
#include "../math_utils/svd_solver.h"
#include "initial_orbit_estimator.h"
#include <vector>

class LeastSquaresDeterminator {
public:
    /**
     * @brief Определяет орбиту кометы методом наименьших квадратов
     * @param observations Вектор наблюдений кометы
     * @return Уточнённые орбитальные элементы
     */
    OrbitalElements determineOrbit(const std::vector<Observation>& observations);
    
private:
    double tolerance_ = 1e-6;
    int max_iterations_ = 50;
    
    // Грубое начальное приближение
    OrbitalElements initialGuess(const std::vector<Observation>& obs);
    
    // Вычисление предсказанных координат
    std::vector<double> calculatePredictedCoordinates(const OrbitalElements& orbit, double jd);
    
    // Вычисление производных для матрицы Якоби
    std::vector<double> computeRADerivatives(const OrbitalElements& orbit, double jd);
    std::vector<double> computeDecDerivatives(const OrbitalElements& orbit, double jd);
    
    // Применение поправок к элементам орбиты
    void applyCorrections(OrbitalElements& orbit, const std::vector<double>& corrections);
    
    // Решение уравнения Кеплера
    double solveKeplerEquation(double M, double e);
    
    // Вспомогательные методы для преобразования координат
    std::vector<double> calculateHeliocentricPosition(const OrbitalElements& orbit, double true_anomaly, double r);
    std::vector<double> cartesianToEquatorial(const std::vector<double>& cartesian);
};