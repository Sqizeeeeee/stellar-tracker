#ifndef OBSERVATION_H
#define OBSERVATION_H

#include <string>

/**
 * @brief Структура для представления астрономического наблюдения кометы
 * 
 * Содержит данные одного наблюдения: дату/время и координаты 
 * во второй экваториальной системе координат
 */
struct Observation {
    /**
     * @brief Юлианская дата момента наблюдения
     * 
     * Используется для точных астрономических вычислений.
     * Более точна чем григорианский календарь для расчётов орбит.
     */
    double julian_date;

    /**
     * @brief Прямое восхождение (Right Ascension) в радианах
     * 
     * Эквивалент долготы на небесной сфере.
     * Диапазон: [0, 2π) радиан
     */
    double right_ascension;

    /**
     * @brief Склонение (Declination) в радианах  
     * 
     * Эквивалент широты на небесной сфере.
     * Диапазон: [-π/2, +π/2] радиан
     */
    double declination;

    /**
     * @brief Проверка валидности данных наблюдения
     * @return true если данные в допустимых диапазонах, иначе false
     */
    bool isValid() const {
        return julian_date > 0 && 
               right_ascension >= 0 && right_ascension < 2 * M_PI &&
               declination >= -M_PI/2 && declination <= M_PI/2;
    }
};

#endif // OBSERVATION_H