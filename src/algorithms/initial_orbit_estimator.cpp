#include "initial_orbit_estimator.h"
#include "fast_orbit_estimator.h"
#include "../math_utils/constants.h"
#include <algorithm>
#include <cmath>
#include <iostream>


OrbitalElements InitialOrbitEstimator::estimateFromObservations(
    const std::vector<Observation>& observations) {
    
    // Используем быстрый эстиматор для точности 5-10%
    return FastOrbitEstimator::estimateWithPrecision(observations);
}

double InitialOrbitEstimator::estimateSemiMajorAxis(
    const std::vector<Observation>& observations) {
    
    // Оцениваем по времени наблюдения и угловой скорости
    double time_span = observations.back().julian_date - observations[0].julian_date;
    double days = time_span;
    
    if (days < 100) return 3.0;   // Короткая дуга: ближние астероиды/кометы
    if (days < 500) return 5.0;   // Средняя дуга: типичные кометы
    return 10.0;                  // Длинная дуга: дальние кометы
}

double InitialOrbitEstimator::estimateEccentricity(
    const std::vector<Observation>& observations) {
    
    // Анализируем "нелинейность" движения
    if (observations.size() < 3) return 0.7;
    
    // Если объект сильно ускоряется/замедляется - высокая эллиптичность
    double ra1 = observations[1].right_ascension - observations[0].right_ascension;
    double ra2 = observations[2].right_ascension - observations[1].right_ascension;
    
    double acceleration = std::abs(ra2 - ra1);
    
    // Эмпирическая формула: больше ускорение → выше эксцентриситет
    return std::min(0.1 + acceleration * 2.0, 0.95);
}

double InitialOrbitEstimator::estimateInclination(
    const std::vector<Observation>& observations) {
    
    // Оцениваем по разбросу склонений
    double min_dec = observations[0].declination;
    double max_dec = observations[0].declination;
    
    for (const auto& obs : observations) {
        min_dec = std::min(min_dec, obs.declination);
        max_dec = std::max(max_dec, obs.declination);
    }
    
    double dec_range = max_dec - min_dec;
    
    // Более точная формула на основе статистики орбит
    double estimated_i = dec_range * 3.0; 
    
    // Ограничиваем разумными пределами
    return std::min(std::max(estimated_i, 0.1), M_PI - 0.1);
}

std::pair<double, double> InitialOrbitEstimator::estimateAngles(
    const std::vector<Observation>& observations) {
    
    // Углы оцениваем по геометрии наблюдений
    size_t mid = observations.size() / 2;
    double Omega = observations[0].right_ascension; // Примерно восходящий узел
    double omega = observations[mid].right_ascension + M_PI/4; // Сдвиг от узла
    
    return {Omega, omega};
}

double InitialOrbitEstimator::estimateTimePerihelion(
    const std::vector<Observation>& observations) {
    
    // Перигелий примерно в середине наблюдений
    size_t mid = observations.size() / 2;
    return observations[mid].julian_date;
}