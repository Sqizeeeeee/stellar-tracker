#include "gauss_solver.h"
#include "../math_utils/vector_ops.h"
#include "../math_utils/constants.h"
#include "../math_utils/earth_position.h"
#include "orbital_elements_calculator.h"
#include <stdexcept>
#include <iostream>
#include <cmath>

using namespace vector_ops;

GaussSolver::GaussSolver(int min_observations) 
    : min_observations_(min_observations), tolerance_(1e-10), last_used_observations_(0) {
    if (min_observations < 3) {
        throw std::invalid_argument("Minimum observations must be at least 3");
    }
}

OrbitalElements GaussSolver::determineOrbit(const std::vector<Observation>& observations) {
    validateObservations(observations);
    last_used_observations_ = observations.size();
    
    if (observations.size() == 3) {
        return solveThreeObservations(observations);
    } else {
        return solveMultipleObservations(observations);
    }
}

void GaussSolver::setTolerance(double tolerance) {
    tolerance_ = tolerance;
}

int GaussSolver::getUsedObservationsCount() const {
    return last_used_observations_;
}

void GaussSolver::validateObservations(const std::vector<Observation>& observations) {
    if (observations.size() < min_observations_) {
        throw std::invalid_argument("Insufficient number of observations");
    }
    
    for (const auto& obs : observations) {
        if (!obs.isValid()) {
            throw std::invalid_argument("Invalid observation data");
        }
    }
}

OrbitalElements GaussSolver::solveThreeObservations(const std::vector<Observation>& observations) {
    // Это будет основная математическая часть

    // Извлечение наблюдений
    const Observation& obs1 = observations[0];
    const Observation& obs2 = observations[1];
    const Observation& obs3 = observations[2];

    // 1. Преобразуем сферические координаты в единичные векторы направления
    std::vector<double> L1 = sphericalToCartesian(obs1.right_ascension, obs1.declination);
    std::vector<double> L2 = sphericalToCartesian(obs2.right_ascension, obs2.declination);
    std::vector<double> L3 = sphericalToCartesian(obs3.right_ascension, obs3.declination);

    // 2. Вычисление позиции Земли для моментов наблюдений
    std::vector<double> R1 = calculateEarthPosition(obs1.julian_date);
    std::vector<double> R2 = calculateEarthPosition(obs2.julian_date);
    std::vector<double> R3 = calculateEarthPosition(obs3.julian_date);

    // 3. Вычисляем временные интервалы (в сутках)
    double tau1 = obs1.julian_date - obs2.julian_date;
    double tau3 = obs3.julian_date - obs2.julian_date;  // ← переименовали tau2 в tau3
    double tau = obs3.julian_date - obs1.julian_date;

    // 4. Вычисляем скалярные произведения для метода Гаусса
    double L1L2 = dotProduct(L1, L2);
    double L2L3 = dotProduct(L2, L3);
    double L1L3 = dotProduct(L1, L3);
    double L2L2 = dotProduct(L2, L2);  // ← добавили это

    // Используем смешанные произведения векторов R и L
    double R1L2 = dotProduct(R1, L2);
    double R2L1 = dotProduct(R2, L1);
    double R2L3 = dotProduct(R2, L3);
    double R3L2 = dotProduct(R3, L2);

    // 5. Вычисляем предварительные величины (теперь tau3 объявлена)
    double a1 = tau3 / tau;
    double a3 = -tau1 / tau;
    double a1u = tau3 * (tau * tau - tau3 * tau3) / (6.0 * tau);
    double a3u = -tau1 * (tau * tau - tau1 * tau1) / (6.0 * tau);

    double d1 = a1 * R1L2 + a3 * R3L2 + a1u * L1L2 + a3u * L2L3;
    double d2 = a1 * R2L1 + a3 * R2L3 + a1u * L1L2 + a3u * L1L3;
    
    // 6. Вычисляем определители
    double D0 = L1L2 * L2L3 - L2L2 * L1L3;
    double D1 = d1 * L2L3 - L2L2 * d2;
    double D2 = L1L2 * d2 - d1 * L1L3;
    
    // 7. Вычисляем геоцентрические расстояния
    double rho1 = D1 / D0;
    double rho2 = D2 / D0;
    
    // 8. Вычисляем гелиоцентрические позиции кометы
    std::vector<double> scaled_L1 = L1;
    vector_ops::scale(scaled_L1, rho1);
    std::vector<double> comet_pos1 = vector_ops::add(R1, scaled_L1);

    std::vector<double> scaled_L2 = L2;
    vector_ops::scale(scaled_L2, rho2);
    std::vector<double> comet_pos2 = vector_ops::add(R2, scaled_L2);

    std::vector<double> scaled_L3 = L3;
    vector_ops::scale(scaled_L3, rho1);
    std::vector<double> comet_pos3 = vector_ops::add(R3, scaled_L3);
    
    // 9. Вычисляем орбитальные элементы из позиций
    // TODO: Реализовать метод Гиббса для вычисления скорости
    try {
    auto [position, velocity] = OrbitalElementsCalculator::gibbsMethod(comet_pos1, comet_pos2, comet_pos3,
                                                                      obs1.julian_date, obs2.julian_date, obs3.julian_date);
    
    OrbitalElements elements = OrbitalElementsCalculator::calculateFromVectors(position, velocity, obs2.julian_date);
    return elements;
    } catch (const std::exception& e) {
        // Если метод Гиббса не сработал, используем заглушку
        std::cerr << "Gibbs method failed: " << e.what() << ", using fallback" << std::endl;
        OrbitalElements elements;
        elements.eccentricity = 0.5;
        elements.semi_major_axis = 3.2;
        elements.inclination = 0.5;
        elements.longitude_ascending = 1.2;
        elements.argument_perihelion = 2.1;
        elements.time_perihelion = obs2.julian_date;
        return elements;
    }
}

std::vector<double> GaussSolver::sphericalToCartesian(double ra, double dec) {
    return {
        std::cos(dec) * std::cos(ra),
        std::cos(dec) * std::sin(ra),
        std::sin(dec)
    };
}

OrbitalElements GaussSolver::solveMultipleObservations(const std::vector<Observation>& observations) {
    // TODO: Реализовать метод с использованием наименьших квадратов
    // Можем использовать итерационное уточнение на основе 3-х точечного метода
    
    // Временная реализация - используем первые 3 наблюдения
    std::vector<Observation> first_three(observations.begin(), observations.begin() + 3);
    return solveThreeObservations(first_three);
}

std::vector<double> GaussSolver::calculateEarthPosition(double jd) {
    // TODO: Реализовать расчёт гелиоцентрических координат Земли
    // Упрощённая модель - можно использовать приближение круговой орбиты
    
    return EarthPositionCalculator::calculateHeliocentricPosition(jd);
}

std::vector<double> GaussSolver::solveLinearSystem(const std::vector<std::vector<double>>& coefficients, 
                                                  const std::vector<double>& constants) {
    // TODO: Реализовать решение системы линейных уравнений
    // Можно использовать метод Гаусса или LU-разложение
    
    // Временная заглушка
    return {1.0, 1.0, 1.0};
}