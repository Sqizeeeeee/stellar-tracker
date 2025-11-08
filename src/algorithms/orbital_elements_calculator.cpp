#include "orbital_elements_calculator.h"
#include "../math_utils/vector_ops.h"
#include "../math_utils/constants.h"
#include <cmath>

using namespace vector_ops;

OrbitalElements OrbitalElementsCalculator::calculateFromVectors(
    const std::vector<double>& position, 
    const std::vector<double>& velocity, 
    double jd) {
    
    OrbitalElements elements;
    
    // 1. Вычисляем удельный момент
    std::vector<double> h = calculateAngularMomentum(position, velocity);
    double h_mag = norm(h);
    
    // 2. Вычисляем вектор Лапласа-Рунге-Ленца
    std::vector<double> e_vec = calculateLaplaceVector(position, velocity, h);
    double e_mag = norm(e_vec);
    
    // 3. Вычисляем энергию и большую полуось
    double r_mag = norm(position);
    double v_mag = norm(velocity);
    double energy = (v_mag * v_mag) / 2.0 - constants::GRAVITATIONAL_CONSTANT / r_mag;
    double a = -constants::GRAVITATIONAL_CONSTANT / (2.0 * energy);
    
    // 4. Вычисляем наклонение
    elements.inclination = acos(h[2] / h_mag);
    
    // 5. Вычисляем долготу восходящего узла
    double omega_x = -h[1];
    double omega_y = h[0];
    elements.longitude_ascending = atan2(omega_y, omega_x);
    if (elements.longitude_ascending < 0) {
        elements.longitude_ascending += constants::TWO_PI;
    }
    
    // 6. Вычисляем аргумент перицентра
    double n_mag = sqrt(omega_x * omega_x + omega_y * omega_y);
    if (n_mag > 0) {
        double cos_w = (omega_x * e_vec[0] + omega_y * e_vec[1]) / (n_mag * e_mag);
        elements.argument_perihelion = acos(cos_w);
        if (e_vec[2] < 0) {
            elements.argument_perihelion = constants::TWO_PI - elements.argument_perihelion;
        }
    } else {
        elements.argument_perihelion = 0.0;
    }
    
    // 7. Записываем вычисленные элементы
    elements.eccentricity = e_mag;
    elements.semi_major_axis = a;
    elements.time_perihelion = jd; // Временное значение
    
    return elements;
}

std::vector<double> OrbitalElementsCalculator::calculateAngularMomentum(
    const std::vector<double>& position, 
    const std::vector<double>& velocity) {
    
    return crossProduct(position, velocity);
}

std::vector<double> OrbitalElementsCalculator::calculateLaplaceVector(
    const std::vector<double>& position, 
    const std::vector<double>& velocity, 
    const std::vector<double>& angular_momentum) {
    
    double r_mag = norm(position);
    std::vector<double> r_unit = position;
    normalize(r_unit);
    
    // Создаем копии для масштабирования
    std::vector<double> term1 = velocity;
    scale(term1, norm(angular_momentum) / constants::GRAVITATIONAL_CONSTANT);
    
    std::vector<double> term2 = r_unit;
    scale(term2, 1.0 / r_mag);
    
    // Используем функцию subtract из vector_ops
    return subtract(term1, term2);
}

std::pair<std::vector<double>, std::vector<double>> 
OrbitalElementsCalculator::gibbsMethod(const std::vector<double>& r1, const std::vector<double>& r2, const std::vector<double>& r3,
                                      double t1, double t2, double t3) {
    
    // 1. Проверяем, что векторы копланарны (лежат в одной плоскости)
    std::vector<double> cross_12_23 = crossProduct(subtract(r2, r1), subtract(r3, r2));
    if (norm(cross_12_23) < 1e-10) {
        throw std::invalid_argument("Vectors are coplanar - cannot use Gibbs method");
    }
    
    // 2. Вычисляем величины Z12, Z32, Z
    std::vector<double> Z12 = crossProduct(r1, r2);
    std::vector<double> Z32 = crossProduct(r3, r2);
    std::vector<double> Z = add(Z12, Z32);
    
    // 3. Вычисляем вектор D
    std::vector<double> D = add(crossProduct(r1, r2), add(crossProduct(r2, r3), crossProduct(r3, r1)));
    
    // 4. Вычисляем вектор S
    double r1_mag = norm(r1);
    double r2_mag = norm(r2); 
    double r3_mag = norm(r3);
    
    // Создаем копии для масштабирования
    std::vector<double> term1 = r1;
    scale(term1, r2_mag - r3_mag);
    
    std::vector<double> term2 = r2;
    scale(term2, r3_mag - r1_mag);
    
    std::vector<double> term3 = r3;
    scale(term3, r1_mag - r2_mag);
    
    std::vector<double> S = add(term1, add(term2, term3));
    
    // 5. Вычисляем вектор B и скаляр L
    std::vector<double> B = crossProduct(D, r2);
    double L = sqrt(constants::GRAVITATIONAL_CONSTANT) / (norm(D) * norm(D));
    
    // 6. Вычисляем вектор скорости
    std::vector<double> B_scaled = B;
    scale(B_scaled, L / r2_mag);
    
    std::vector<double> S_scaled = S;
    scale(S_scaled, L);
    
    std::vector<double> velocity = add(B_scaled, S_scaled);
    
    return {r2, velocity};
}