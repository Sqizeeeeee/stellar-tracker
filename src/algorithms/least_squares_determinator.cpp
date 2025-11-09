#include "least_squares_determinator.h"
#include "../math_utils/earth_position.h"
#include "../math_utils/constants.h"
#include <cmath>
#include <iostream>

OrbitalElements LeastSquaresDeterminator::determineOrbit(
    const std::vector<Observation>& observations) {
    
    // 1. Получаем грубое начальное приближение
    OrbitalElements current_orbit = initialGuess(observations);
    
    // 2. Итеративное уточнение методом наименьших квадратов
    for (int iter = 0; iter < max_iterations_; ++iter) {
        // Создаем матрицу Якоби и вектор невязок
        std::vector<std::vector<double>> jacobian;
        std::vector<double> residuals;
        
        // Для каждого наблюдения вычисляем невязку и производные
        for (const auto& obs : observations) {
            // Вычисляем предсказанные координаты для текущей орбиты
            std::vector<double> predicted = calculatePredictedCoordinates(current_orbit, obs.julian_date);
            
            // Вычисляем невязку (разность предсказанных и реальных координат)
            double ra_residual = predicted[0] - obs.right_ascension;
            double dec_residual = predicted[1] - obs.declination;
            
            // Добавляем невязки в вектор
            residuals.push_back(ra_residual);
            residuals.push_back(dec_residual);
            
            // Вычисляем производные невязки по параметрам орбиты
            std::vector<double> ra_derivs = computeRADerivatives(current_orbit, obs.julian_date);
            std::vector<double> dec_derivs = computeDecDerivatives(current_orbit, obs.julian_date);
            
            // Добавляем строки в матрицу Якоби
            jacobian.push_back(ra_derivs);
            jacobian.push_back(dec_derivs);
        }
        
        // Решаем систему методом наименьших квадратов
        std::vector<double> corrections = SVDSolver::solveLeastSquares(jacobian, residuals);
        
        // Применяем поправки к элементам орбиты
        applyCorrections(current_orbit, corrections);
        
        // Проверка сходимости (норма поправок мала)
        double correction_norm = 0;
        for (double corr : corrections) correction_norm += corr * corr;
        if (std::sqrt(correction_norm) < tolerance_) {
            std::cout << "Сходимость достигнута на итерации " << iter + 1 << std::endl;
            break;
        }
    }
    
    return current_orbit;
}


std::vector<double> LeastSquaresDeterminator::calculatePredictedCoordinates(
    const OrbitalElements& orbit, double jd) {
    
    // 1. Вычисляем позицию Земли
    std::vector<double> earth_pos = EarthPositionCalculator::calculateHeliocentricPosition(jd);
    
    double true_anomaly, r;
    
    // Разные формулы для разных типов орбит
    if (orbit.eccentricity < 1.0) {
        // Эллиптическая орбита
        double n = sqrt(constants::GM_SUN / pow(orbit.semi_major_axis, 3));
        double M = n * (jd - orbit.time_perihelion);
        double E = solveKeplerEquation(M, orbit.eccentricity);
        true_anomaly = 2 * atan2(sqrt(1 + orbit.eccentricity) * sin(E/2), 
                                sqrt(1 - orbit.eccentricity) * cos(E/2));
        r = orbit.semi_major_axis * (1 - orbit.eccentricity * cos(E));
    } else {
        // Для начального приближения используем упрощенный расчет
        // Предполагаем, что комета движется равномерно по прямой
        double mean_motion = 0.1; // Произвольная скорость
        true_anomaly = mean_motion * (jd - orbit.time_perihelion);
        r = orbit.semi_major_axis;
    }
    
    // Остальной код без изменений...
    std::vector<double> comet_pos = calculateHeliocentricPosition(orbit, true_anomaly, r);
    std::vector<double> geo_pos = {
        comet_pos[0] - earth_pos[0],
        comet_pos[1] - earth_pos[1], 
        comet_pos[2] - earth_pos[2]
    };
    return cartesianToEquatorial(geo_pos);
}

std::vector<double> LeastSquaresDeterminator::computeRADerivatives(
    const OrbitalElements& orbit, double jd) {
    // Численное дифференцирование
    std::vector<double> derivatives(6, 0.0);
    double delta = 1e-8;
    
    for (int i = 0; i < 6; ++i) {
        OrbitalElements orbit_plus = orbit;
        OrbitalElements orbit_minus = orbit;
        
        // Применяем малую вариацию к i-му параметру
        switch(i) {
            case 0: orbit_plus.semi_major_axis += delta; orbit_minus.semi_major_axis -= delta; break;
            case 1: orbit_plus.eccentricity += delta; orbit_minus.eccentricity -= delta; break;
            case 2: orbit_plus.inclination += delta; orbit_minus.inclination -= delta; break;
            case 3: orbit_plus.longitude_ascending += delta; orbit_minus.longitude_ascending -= delta; break;
            case 4: orbit_plus.argument_perihelion += delta; orbit_minus.argument_perihelion -= delta; break;
            case 5: orbit_plus.time_perihelion += delta; orbit_minus.time_perihelion -= delta; break;
        }
        
        double ra_plus = calculatePredictedCoordinates(orbit_plus, jd)[0];
        double ra_minus = calculatePredictedCoordinates(orbit_minus, jd)[0];
        derivatives[i] = (ra_plus - ra_minus) / (2 * delta);
    }
    
    return derivatives;
}

std::vector<double> LeastSquaresDeterminator::computeDecDerivatives(
    const OrbitalElements& orbit, double jd) {
    std::vector<double> derivatives(6, 0.0);
    double delta = 1e-8;
    
    for (int i = 0; i < 6; ++i) {
        OrbitalElements orbit_plus = orbit;
        OrbitalElements orbit_minus = orbit;
        
        // Применяем малую вариацию к i-му параметру
        switch(i) {
            case 0: orbit_plus.semi_major_axis += delta; orbit_minus.semi_major_axis -= delta; break;
            case 1: orbit_plus.eccentricity += delta; orbit_minus.eccentricity -= delta; break;
            case 2: orbit_plus.inclination += delta; orbit_minus.inclination -= delta; break;
            case 3: orbit_plus.longitude_ascending += delta; orbit_minus.longitude_ascending -= delta; break;
            case 4: orbit_plus.argument_perihelion += delta; orbit_minus.argument_perihelion -= delta; break;
            case 5: orbit_plus.time_perihelion += delta; orbit_minus.time_perihelion -= delta; break;
        }
        
        double dec_plus = calculatePredictedCoordinates(orbit_plus, jd)[1];
        double dec_minus = calculatePredictedCoordinates(orbit_minus, jd)[1];
        derivatives[i] = (dec_plus - dec_minus) / (2 * delta);
    }
    
    return derivatives;
}

void LeastSquaresDeterminator::applyCorrections(
    OrbitalElements& orbit, const std::vector<double>& corrections) {
    
    // УНИВЕРСАЛЬНЫЕ ограничения для всех небесных тел
    double max_correction = 0.1; // Общий предел
    
    // Разные пределы для разных параметров (физически обоснованные)
    orbit.semi_major_axis -= std::min(std::max(corrections[0], -max_correction), max_correction);
    orbit.eccentricity    -= std::min(std::max(corrections[1], -0.05), 0.05); // e меняется медленнее
    orbit.inclination     -= std::min(std::max(corrections[2], -0.05), 0.05); // i меняется медленнее
    
    // УГЛЫ - более жесткие ограничения (часто плохо обусловлены)
    orbit.longitude_ascending -= std::min(std::max(corrections[3], -0.02), 0.02);
    orbit.argument_perihelion -= std::min(std::max(corrections[4], -0.02), 0.02);
    
    orbit.time_perihelion -= std::min(std::max(corrections[5], -10.0), 10.0); // Время - в днях
    
    // ФИЗИЧЕСКИЕ ПРЕДЕЛЫ для всех комет/астероидов
    orbit.eccentricity = std::max(orbit.eccentricity, 0.0);
    orbit.semi_major_axis = std::max(orbit.semi_major_axis, 0.1);
    orbit.inclination = std::min(std::max(orbit.inclination, 0.01), M_PI - 0.01);
    
    // Нормализация углов
    orbit.longitude_ascending = fmod(orbit.longitude_ascending, 2 * M_PI);
    if (orbit.longitude_ascending < 0) orbit.longitude_ascending += 2 * M_PI;
    orbit.argument_perihelion = fmod(orbit.argument_perihelion, 2 * M_PI);
    if (orbit.argument_perihelion < 0) orbit.argument_perihelion += 2 * M_PI;
}

double LeastSquaresDeterminator::solveKeplerEquation(double M, double e) {
    double E = M; // Начальное приближение
    for (int i = 0; i < 10; ++i) {
        double delta = (E - e * sin(E) - M) / (1 - e * cos(E));
        E -= delta;
        if (fabs(delta) < 1e-12) break;
    }
    return E;
}

std::vector<double> LeastSquaresDeterminator::calculateHeliocentricPosition(
    const OrbitalElements& orbit, double true_anomaly, double r) {
    // Вычисляем гелиоцентрические координаты в орбитальной плоскости
    double x_orb = r * cos(true_anomaly);
    double y_orb = r * sin(true_anomaly);
    
    // Преобразуем в гелиоцентрические эклиптические координаты
    double cos_omega = cos(orbit.argument_perihelion);
    double sin_omega = sin(orbit.argument_perihelion);
    double cos_Omega = cos(orbit.longitude_ascending);
    double sin_Omega = sin(orbit.longitude_ascending);
    double cos_i = cos(orbit.inclination);
    double sin_i = sin(orbit.inclination);
    
    std::vector<double> position(3);
    position[0] = x_orb * (cos_omega * cos_Omega - sin_omega * sin_Omega * cos_i) -
                  y_orb * (sin_omega * cos_Omega + cos_omega * sin_Omega * cos_i);
    
    position[1] = x_orb * (cos_omega * sin_Omega + sin_omega * cos_Omega * cos_i) -
                  y_orb * (sin_omega * sin_Omega - cos_omega * cos_Omega * cos_i);
    
    position[2] = x_orb * (sin_omega * sin_i) + y_orb * (cos_omega * sin_i);
    
    return position;
}

std::vector<double> LeastSquaresDeterminator::cartesianToEquatorial(
    const std::vector<double>& ecliptic_cartesian) {
    
    // Угол наклона эклиптики к экватору (ε) для эпохи J2000
    double epsilon = 23.43928 * M_PI / 180.0;
    
    double x_ecl = ecliptic_cartesian[0];
    double y_ecl = ecliptic_cartesian[1]; 
    double z_ecl = ecliptic_cartesian[2];
    
    // Преобразование эклиптических → экваториальные координаты
    double x_eq = x_ecl;
    double y_eq = y_ecl * cos(epsilon) - z_ecl * sin(epsilon);
    double z_eq = y_ecl * sin(epsilon) + z_ecl * cos(epsilon);
    
    // Преобразование в сферические (RA, Dec)
    double ra = atan2(y_eq, x_eq);
    if (ra < 0) ra += 2 * M_PI;
    
    double dec = atan2(z_eq, sqrt(x_eq*x_eq + y_eq*y_eq));
    
    return {ra, dec};
}

OrbitalElements LeastSquaresDeterminator::initialGuess(
    const std::vector<Observation>& obs) {
    
    // Используем новый точный estimator вместо грубого приближения
    return InitialOrbitEstimator::estimateFromObservations(obs);
}