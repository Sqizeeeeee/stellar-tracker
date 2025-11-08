#include "earth_position.h"
#include <cmath>

std::vector<double> EarthPositionCalculator::calculateHeliocentricPosition(double jd) {
    // Вычисляем время в юлианских столетиях от эпохи J2000.0
    double t = (jd - 2451545.0) / 36525.0;
    
    // Орбитальные элементы Земли (упрощённые из VSOP87)
    double L0 = 1.75347045673 + 0.00000000000 * t;  // средняя долгота
    double L1 = 6283.0758499914 * t;                // среднее движение
    
    double L = L0 + L1;
    
    // Эксцентриситет орбиты
    double e = 0.0167086342 - 0.000042037 * t;
    
    // Вычисляем истинную аномалию через уравнение Кеплера (упрощённо)
    double M = L; // для упрощения считаем M ≈ L
    double anomaly = M + 2.0 * e * sin(M) + 1.25 * e * e * sin(2.0 * M);
    
    // Расстояние (а.е.)
    double r = 1.0000010178 * (1.0 - e * e) / (1.0 + e * cos(anomaly));
    
    // Эклиптические координаты
    double lon = anomaly + 1.796601474; // +102.93734808° в радианах
    
    // Преобразуем в декартовы координаты (эклиптическая система)
    double x = r * cos(lon);
    double y = r * sin(lon);
    double z = 0.0; // Земля близка к плоскости эклиптики
    
    return {x, y, z};
}

std::vector<double> EarthPositionCalculator::calculateEclipticCoordinates(double jd) {
    auto pos = calculateHeliocentricPosition(jd);
    double x = pos[0], y = pos[1], z = pos[2];
    
    double distance = sqrt(x*x + y*y + z*z);
    double lon = atan2(y, x);
    double lat = asin(z / distance);
    
    if (lon < 0) lon += constants::TWO_PI;
    
    return {lon, lat, distance};
}

std::vector<double> EarthPositionCalculator::calculateOrbitalElements(double t) {
    // Упрощённые орбитальные элементы Земли
    double L = 1.75347045673 + 6283.0758499914 * t;  // средняя долгота
    double a = 1.0000010178;                         // большая полуось (а.е.)
    double e = 0.0167086342 - 0.000042037 * t;       // эксцентриситет
    double i = 0.0;                                  // наклонение
    double omega = 0.0;                              // долгота восходящего узла
    double w = 1.796601474;                          // аргумент перицентра
    
    return {L, a, e, i, omega, w};
}