#ifndef ORBITAL_ELEMENTS_H
#define ORBITAL_ELEMENTS_H

#include <string>
#include "../math_utils/constants.h"

/**
 * @brief Структура для представления орбитальных элементов кометы
 * 
 * Содержит классические кеплеровы элементы орбиты
 * в гелиоцентрической системе координат
 */
struct OrbitalElements {
    /**
     * @brief Эксцентриситет орбиты
     * 
     * Определяет форму орбиты:
     * e = 0 - круговая орбита
     * 0 < e < 1 - эллиптическая орбита  
     * e = 1 - параболическая орбита
     * e > 1 - гиперболическая орбита
     */
    double eccentricity;

    /**
     * @brief Большая полуось орбиты в астрономических единицах (а.е.)
     * 
     * Характеризует размер орбиты.
     * 1 а.е. = среднее расстояние Земля-Солнце (~149.6 млн км)
     */
    double semi_major_axis;

    /**
     * @brief Наклонение орбиты в радианах
     * 
     * Угол между плоскостью орбиты и плоскостью эклиптики.
     * Диапазон: [0, π] радиан
     */
    double inclination;

    /**
     * @brief Долгота восходящего узла в радианах
     * 
     * Угол между направлением на точку весеннего равноденствия 
     * и восходящим узлом орбиты.
     * Диапазон: [0, 2π) радиан
     */
    double longitude_ascending;

    /**
     * @brief Аргумент перицентра в радианах
     * 
     * Угол между восходящим узлом и направлением на перицентр.
     * Диапазон: [0, 2π) радиан
     */
    double argument_perihelion;

    /**
     * @brief Время прохождения перицентра в юлианских днях
     * 
     * Момент, когда комета находится ближе всего к Солнцу.
     */
    double time_perihelion;

    /**
     * @brief Проверка физической валидности орбитальных элементов
     * @return true если элементы физически корректны, иначе false
     */
    bool isValid() const {
        return eccentricity >= 0 &&
               semi_major_axis > 0 &&
               inclination >= 0 && inclination <= M_PI &&
               longitude_ascending >= 0 && longitude_ascending < 2 * M_PI &&
               argument_perihelion >= 0 && argument_perihelion < 2 * M_PI &&
               time_perihelion > 0;
    }
};

#endif // ORBITAL_ELEMENTS_H