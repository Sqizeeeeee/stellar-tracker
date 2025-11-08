#ifndef EARTH_POSITION_H
#define EARTH_POSITION_H

#include <vector>
#include "constants.h"

/**
 * @brief Класс для точного расчёта гелиоцентрических координат Земли
 * 
 * Использует приближённые формулы VSOP87 для вычисления позиции Земли
 * с точностью достаточной для определения орбит комет
 */
class EarthPositionCalculator {
public:
    /**
     * @brief Вычисляет гелиоцентрические координаты Земли на заданную юлианскую дату
     * @param jd Юлианская дата
     * @return Вектор [x, y, z] координат Земли в астрономических единицах (а.е.)
     */
    static std::vector<double> calculateHeliocentricPosition(double jd);
    
    /**
     * @brief Вычисляет эклиптические координаты Земли (долготу, широту, расстояние)
     * @param jd Юлианская дата
     * @return Вектор [долгота, широта, расстояние] в радианах и а.е.
     */
    static std::vector<double> calculateEclipticCoordinates(double jd);
    
private:
    /**
     * @brief Вычисляет орбитальные элементы Земли на заданную эпоху
     * @param t Время в юлианских столетиях от эпохи J2000.0
     * @return Вектор орбитальных элементов [L, a, e, i, Ω, ω]
     */
    static std::vector<double> calculateOrbitalElements(double t);
};

#endif // EARTH_POSITION_H