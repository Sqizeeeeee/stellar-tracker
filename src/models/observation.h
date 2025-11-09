#ifndef OBSERVATION_H
#define OBSERVATION_H

#include <string>

/**
 * @brief Структура для представления астрономического наблюдения
 * 
 * Содержит данные одного наблюдения: дату/время, координаты
 * во второй экваториальной системе координат и тип небесного тела
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
     * @brief Тип небесного тела
     * 
     * Определяет стратегию оценки начального приближения орбиты.
     * Допустимые значения: "comet", "asteroid", "planet"
     */
    std::string object_type;

    /**
     * @brief Проверка валидности данных наблюдения
     * @return true если данные в допустимых диапазонах, иначе false
     */
    bool isValid() const {
        bool valid_coordinates = julian_date > 0 && 
                               right_ascension >= 0 && right_ascension < 2 * M_PI &&
                               declination >= -M_PI/2 && declination <= M_PI/2;
        
        bool valid_type = object_type == "comet" || 
                         object_type == "asteroid" || 
                         object_type == "planet" ||
                         object_type.empty(); // Пустой тип тоже допустим
        
        return valid_coordinates && valid_type;
    }

    /**
     * @brief Проверяет является ли объект кометой
     * @return true если object_type == "comet"
     */
    bool isComet() const {
        return object_type == "comet";
    }

    /**
     * @brief Проверяет является ли объект астероидом
     * @return true если object_type == "asteroid"
     */
    bool isAsteroid() const {
        return object_type == "asteroid";
    }

    /**
     * @brief Проверяет является ли объект планетой
     * @return true если object_type == "planet"
     */
    bool isPlanet() const {
        return object_type == "planet";
    }
};

#endif // OBSERVATION_H