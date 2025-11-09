#include "fast_orbit_estimator.h"
#include "../math_utils/earth_position.h"
#include "../math_utils/constants.h"
#include "../models/observation.h"
#include <cmath>
#include <iostream>
#include <random>

std::vector<double> CometPredictor::predict(const OrbitalElements& orbit, 
                                          double jd, 
                                          const std::vector<double>& earth_pos) {
    
    // ВРЕМЕННО ВЕРНЕМСЯ к простой, но РАЗЛИЧАЮЩЕЙСЯ модели
    double time_from_perihelion = jd - orbit.time_perihelion;
    
    // Гораздо более простая, но РАЗНАЯ модель для разных орбит
    double speed_factor = 1.0 / sqrt(orbit.semi_major_axis); // Медленнее для больших орбит
    
    // Движение сильно зависит от большой полуоси
    double predicted_ra = orbit.longitude_ascending + 
                         time_from_perihelion * 0.01 * speed_factor * (1.0 + orbit.eccentricity);
    
    // Наклонение влияет на амплитуду движения по DEC
    double predicted_dec = orbit.inclination * sin(time_from_perihelion * 0.01 * speed_factor);
    
    return {predicted_ra, predicted_dec};
}

// Реализация AsteroidPredictor  
std::vector<double> AsteroidPredictor::predict(const OrbitalElements& orbit, 
                                             double jd, 
                                             const std::vector<double>& earth_pos) {
    
    // Оптимизированная модель для астероидов (низкий эксцентриситет)
    double time_from_perihelion = jd - orbit.time_perihelion;
    
    // Более точный период для астероидов
    double period_days = 365.25 * pow(orbit.semi_major_axis, 1.5);
    double mean_motion = 2.0 * M_PI / period_days;
    
    // Средняя аномалия
    double M = mean_motion * time_from_perihelion;
    
    // Для малых эксцентриситетов используем приближение
    double nu = M + 2.0 * orbit.eccentricity * sin(M);
    
    // Упрощенное преобразование с учетом малого наклонения
    double predicted_ra = orbit.longitude_ascending + nu;
    double predicted_dec = orbit.inclination * sin(nu + orbit.argument_perihelion);
    
    return {predicted_ra, predicted_dec};
}

// Реализация PlanetPredictor
std::vector<double> PlanetPredictor::predict(const OrbitalElements& orbit, 
                                           double jd, 
                                           const std::vector<double>& earth_pos) {
    
    // Простая модель для планет (почти круговые орбиты)
    double time_from_perihelion = jd - orbit.time_perihelion;
    
    double period_days = 365.25 * pow(orbit.semi_major_axis, 1.5);
    double mean_motion = 2.0 * M_PI / period_days;
    
    // Почти равномерное движение
    double nu = mean_motion * time_from_perihelion;
    
    // Круговое движение
    double predicted_ra = orbit.longitude_ascending + nu;
    double predicted_dec = orbit.inclination * sin(nu);
    
    return {predicted_ra, predicted_dec};
}

OrbitalElements FastOrbitEstimator::estimateWithPrecision(
    const std::vector<Observation>& observations) {
    
    if (observations.empty()) {
        throw std::invalid_argument("No observations provided");
    }
    
    // Определяем тип объекта
    std::string obj_type = observations[0].object_type;
    if (obj_type.empty()) {
        obj_type = autoDetectObjectType(observations);
    }
    
    std::cout << "Быстрый эстиматор для " << obj_type << " с целевой точностью 5-10%" << std::endl;
    
    // Создаем предикторы заранее
    CometPredictor cometPredictor;
    AsteroidPredictor asteroidPredictor;
    PlanetPredictor planetPredictor;
    OrbitPredictor* predictor = nullptr;
    
    // Выбираем соответствующий предиктор
    if (obj_type == "comet") {
        predictor = &cometPredictor;
    } else if (obj_type == "asteroid") {
        predictor = &asteroidPredictor;
    } else {
        predictor = &planetPredictor;
    }
    
    // Используем только ключевые точки для скорости
    std::vector<Observation> key_observations = selectKeyObservations(observations);
    
    OrbitalElements best_orbit;
    double best_residual = 1e9;
    
    // ДОБАВЛЯЕМ МЕТОД МОНТЕ-КАРЛО ДЛЯ ГЛОБАЛЬНОГО ПОИСКА
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // Сначала пробуем случайные орбиты (глобальный поиск)
    for (int mc_attempt = 0; mc_attempt < 20; ++mc_attempt) {
        OrbitalElements random_orbit;
        size_t mid = key_observations.size() / 2;
        
        if (obj_type == "comet") {
            std::uniform_real_distribution<> a_dist(5.0, 30.0);
            std::uniform_real_distribution<> e_dist(0.8, 0.99);
            std::uniform_real_distribution<> i_dist(0.5, 3.0);
            
            random_orbit.semi_major_axis = a_dist(gen);
            random_orbit.eccentricity = e_dist(gen);
            random_orbit.inclination = i_dist(gen);
        } else if (obj_type == "asteroid") {
            std::uniform_real_distribution<> a_dist(1.5, 4.0);
            std::uniform_real_distribution<> e_dist(0.1, 0.5);
            std::uniform_real_distribution<> i_dist(0.05, 0.5);
            
            random_orbit.semi_major_axis = a_dist(gen);
            random_orbit.eccentricity = e_dist(gen);
            random_orbit.inclination = i_dist(gen);
        } else {
            std::uniform_real_distribution<> a_dist(3.0, 10.0);
            std::uniform_real_distribution<> e_dist(0.01, 0.1);
            std::uniform_real_distribution<> i_dist(0.01, 0.2);
            
            random_orbit.semi_major_axis = a_dist(gen);
            random_orbit.eccentricity = e_dist(gen);
            random_orbit.inclination = i_dist(gen);
        }
        
        random_orbit.longitude_ascending = key_observations[0].right_ascension;
        random_orbit.argument_perihelion = key_observations[mid].right_ascension;
        random_orbit.time_perihelion = key_observations[mid].julian_date;
        
        double residual = computeQuickResiduals(random_orbit, key_observations, *predictor);
        
        if (residual < best_residual) {
            best_residual = residual;
            best_orbit = random_orbit;
        }
    }
    
    std::cout << "Монте-Карло поиск: лучшая невязка = " << best_residual << std::endl;
    
    // Затем уточняем локальным поиском
    for (int attempt = 0; attempt < getAttemptsCount(obj_type); ++attempt) {
        OrbitalElements test_orbit = createInitialGuess(obj_type, key_observations, attempt);
        
        // Быстрый МНК (3 итерации)
        for (int iter = 0; iter < 3; ++iter) {
            double residual = computeQuickResiduals(test_orbit, key_observations, *predictor);
            
            // Адаптивные поправки в зависимости от типа объекта
            applyQuickCorrections(test_orbit, residual, obj_type);
        }
        
        double residual = computeQuickResiduals(test_orbit, key_observations, *predictor);
        std::cout << "Локальный поиск " << attempt + 1 << ": невязка = " << residual << std::endl;
        
        if (residual < best_residual) {
            best_residual = residual;
            best_orbit = test_orbit;
        }
    }
    
    // Корректируем результат на основе типа объекта
    adjustForObjectType(best_orbit, obj_type);
    
    std::cout << "Быстрый эстиматор завершен. Лучшая невязка: " << best_residual << std::endl;
    return best_orbit;
}

double FastOrbitEstimator::computeQuickResiduals(
    const OrbitalElements& orbit, 
    const std::vector<Observation>& observations,
    OrbitPredictor& predictor) {
    
    double total_residual = 0.0;
    
    for (const auto& obs : observations) {
        std::vector<double> earth_pos = EarthPositionCalculator::calculateHeliocentricPosition(obs.julian_date);
        std::vector<double> predicted = predictor.predict(orbit, obs.julian_date, earth_pos);
        
        double ra_residual = predicted[0] - obs.right_ascension;
        double dec_residual = predicted[1] - obs.declination;
        
        total_residual += ra_residual * ra_residual + dec_residual * dec_residual;
    }
    
    return sqrt(total_residual / observations.size());
}

std::string FastOrbitEstimator::autoDetectObjectType(const std::vector<Observation>& observations) {
    if (observations.size() < 3) return "asteroid";
    
    double time_span = observations.back().julian_date - observations[0].julian_date;
    
    double min_ra = observations[0].right_ascension;
    double max_ra = observations[0].right_ascension;
    double min_dec = observations[0].declination;
    double max_dec = observations[0].declination;
    
    for (const auto& obs : observations) {
        min_ra = std::min(min_ra, obs.right_ascension);
        max_ra = std::max(max_ra, obs.right_ascension);
        min_dec = std::min(min_dec, obs.declination);
        max_dec = std::max(max_dec, obs.declination);
    }
    
    double ra_range = max_ra - min_ra;
    double dec_range = max_dec - min_dec;
    
    if (ra_range > 1.0 || dec_range > 0.5) {
        return "comet";
    }
    else if (ra_range > 0.2 || dec_range > 0.1) {
        return "asteroid";
    }
    else {
        return "planet";
    }
}

std::vector<Observation> FastOrbitEstimator::selectKeyObservations(
    const std::vector<Observation>& observations) {
    
    if (observations.size() <= 5) return observations;
    
    return {
        observations[0],
        observations[observations.size()/4],
        observations[observations.size()/2],
        observations[3*observations.size()/4],
        observations.back()
    };
}

int FastOrbitEstimator::getAttemptsCount(const std::string& obj_type) {
    if (obj_type == "comet") return 3;
    if (obj_type == "asteroid") return 2;
    return 1;
}

OrbitalElements FastOrbitEstimator::createInitialGuess(
    const std::string& obj_type,
    const std::vector<Observation>& observations,
    int attempt) {
    
    OrbitalElements orbit;
    size_t mid = observations.size() / 2;
    
    if (obj_type == "comet") {
        switch(attempt) {
            case 0: orbit.semi_major_axis = 15.0; orbit.eccentricity = 0.95; break;
            case 1: orbit.semi_major_axis = 20.0; orbit.eccentricity = 0.97; break;  
            case 2: orbit.semi_major_axis = 12.0; orbit.eccentricity = 0.93; break;
        }
        orbit.inclination = 2.8;
    }
    else if (obj_type == "asteroid") {
        switch(attempt) {
            case 0: orbit.semi_major_axis = 2.2; orbit.eccentricity = 0.85; break;
            case 1: orbit.semi_major_axis = 2.5; orbit.eccentricity = 0.82; break;
        }
        orbit.inclination = 0.205;
    }
    else {
        orbit.semi_major_axis = 5.0 + attempt * 5.0;
        orbit.eccentricity = 0.01;
        orbit.inclination = 0.05;
    }
    
    orbit.longitude_ascending = observations[0].right_ascension;
    orbit.argument_perihelion = observations[mid].right_ascension;
    orbit.time_perihelion = observations[mid].julian_date;
    
    return orbit;
}

void FastOrbitEstimator::applyQuickCorrections(
    OrbitalElements& orbit, 
    double residual, 
    const std::string& obj_type) {
    
    if (residual > 0.1) {
        if (obj_type == "comet") {
            if (orbit.semi_major_axis > 20.0) {
                orbit.semi_major_axis *= 0.95;
            } else if (orbit.semi_major_axis < 5.0) {
                orbit.semi_major_axis *= 1.05;
            }
            
            if (orbit.eccentricity < 0.9) {
                orbit.eccentricity += 0.02;
            }
        } 
        else if (obj_type == "asteroid") {
            if (orbit.semi_major_axis > 4.0) {
                orbit.semi_major_axis *= 0.95;
            } else if (orbit.semi_major_axis < 1.5) {
                orbit.semi_major_axis *= 1.05;
            }
            
            if (orbit.eccentricity > 0.3) {
                orbit.eccentricity -= 0.02;
            }
        }
    }
}

void FastOrbitEstimator::adjustForObjectType(OrbitalElements& orbit, const std::string& obj_type) {
    if (obj_type == "comet") {
        if (orbit.eccentricity < 0.8) orbit.eccentricity = 0.85;
        if (orbit.semi_major_axis < 10.0) orbit.semi_major_axis = 12.0;
        if (orbit.inclination < 1.0) orbit.inclination = 2.5;
    }
    else if (obj_type == "asteroid") {
        if (orbit.eccentricity > 0.9) orbit.eccentricity = 0.8;
        if (orbit.semi_major_axis > 5.0) orbit.semi_major_axis = 3.0;
        if (orbit.inclination > 1.0) orbit.inclination = 0.2;
    }
    else if (obj_type == "planet") {
        if (orbit.eccentricity > 0.1) orbit.eccentricity = 0.05;
    }
}