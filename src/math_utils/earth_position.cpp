#include "earth_position.h"
#include <cmath>

/**
 * @brief Вычисляет гелиоцентрические координаты Земли на заданную юлианскую дату
 * @param jd Юлианская дата
 * @return Вектор [x, y, z] координат Земли в астрономических единицах (а.е.)
 */
std::vector<double> EarthPositionCalculator::calculateHeliocentricPosition(double jd) {
    //brief: Вычисляем время в юлианских столетиях от эпохи J2000.0
    double t = (jd - 2451545.0) / 36525.0;
    
    //brief: Улучшенные орбитальные элементы Земли (VSOP87 упрощённые)
    double L0 = 1.75347045673 + 0.00000000000 * t;   // средняя долгота
    double L1 = 6283.0758499914 * t;                 // среднее движение
    
    double L = L0 + L1;
    
    //brief: Эксцентриситет орбиты
    double e = 0.0167086342 - 0.000042037 * t;
    
    //brief: Наклонение орбиты Земли (~0.00005 рад ≈ 0.0029°)
    double i = 0.00005; 
    
    //brief: Долгота восходящего узла (очень медленно меняется)
    double omega = 0.0;
    
    //brief: Аргумент перицентра
    double w = 1.796601474;
    
    //brief: Вычисляем истинную аномалию через уравнение Кеплера
    double M = L; // Упрощение: M ≈ L
    double E = M + e * sin(M) * (1.0 + e * cos(M)); // Приближённое решение Кеплера
    double anomaly = 2.0 * atan(sqrt((1.0 + e) / (1.0 - e)) * tan(E / 2.0));
    
    //brief: Расстояние (а.е.)
    double r = 1.0000010178 * (1.0 - e * e) / (1.0 + e * cos(anomaly));
    
    //brief: Эклиптическая долгота
    double lon = anomaly + w;
    
    //brief: Преобразуем в декартовы координаты с учётом наклонения
    double x = r * (cos(lon) * cos(omega) - sin(lon) * sin(omega) * cos(i));
    double y = r * (cos(lon) * sin(omega) + sin(lon) * cos(omega) * cos(i));
    double z = r * sin(lon) * sin(i);
    
    return {x, y, z};
}

/**
 * @brief Вычисляет эклиптические координаты Земли (долготу, широту, расстояние)
 * @param jd Юлианская дата
 * @return Вектор [долгота, широта, расстояние] в радианах и а.е.
 */
std::vector<double> EarthPositionCalculator::calculateEclipticCoordinates(double jd) {
    auto pos = calculateHeliocentricPosition(jd);
    double x = pos[0], y = pos[1], z = pos[2];
    
    double distance = sqrt(x*x + y*y + z*z);
    double lon = atan2(y, x);
    double lat = atan2(z, sqrt(x*x + y*y)); // Более точное вычисление широты
    
    if (lon < 0) lon += constants::TWO_PI;
    
    return {lon, lat, distance};
}

/**
 * @brief Вычисляет орбитальные элементы Земли на заданную эпоху
 * @param t Время в юлианских столетиях от эпохи J2000.0
 * @return Вектор орбитальных элементов [L, a, e, i, Ω, ω]
 */
std::vector<double> EarthPositionCalculator::calculateOrbitalElements(double t) {
    //brief: Улучшенные орбитальные элементы Земли
    double L = 1.75347045673 + 6283.0758499914 * t;  // средняя долгота
    double a = 1.0000010178;                         // большая полуось (а.е.)
    double e = 0.0167086342 - 0.000042037 * t;       // эксцентриситет
    double i = 0.00005;                              // наклонение (~0.0029°)
    double omega = 0.0;                              // долгота восходящего узла
    double w = 1.796601474;                          // аргумент перицентра
    
    return {L, a, e, i, omega, w};
}