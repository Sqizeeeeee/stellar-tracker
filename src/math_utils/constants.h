#ifndef CONSTANTS_H
#define CONSTANTS_H

/**
 * @brief Пространство имён для математических и астрономических констант
 */
namespace constants {
    /**
     * @brief Число π с двойной точностью
     */
    constexpr double PI = 3.14159265358979323846;
    
    /**
     * @brief 2π (полный угол в радианах)
     */
    constexpr double TWO_PI = 2.0 * PI;
    
    /**
     * @brief π/2 (прямой угол в радианах)
     */
    constexpr double HALF_PI = PI / 2.0;
    
    /**
     * @brief Астрономическая единица в километрах
     * 
     * Среднее расстояние от Земли до Солнца
     */
    constexpr double AU = 149597870.7;
    
    /**
     * @brief Гравитационная постоянная в а.е.³ / (сутки² * масс Солнца)
     * 
     * Используется в орбитальной механике для расчётов в астрономических единицах
     */
    constexpr double GRAVITATIONAL_CONSTANT = 0.00029591220828559104;
    
    /**
     * @brief Скорость света в км/с
     */
    constexpr double SPEED_OF_LIGHT = 299792.458;
    
    /**
     * @brief Угловая скорость Земли в радианах/сутки
     */
    constexpr double EARTH_ANGULAR_VELOCITY = 6.300388098;

    /**
     * @brief Гравитационный параметр Солнца (GM) в а.е.³/сутки²
     * 
     * Используется для расчётов орбит вокруг Солнца
     */
    constexpr double GM_SUN = 0.00029591220828559104;
}

#endif // CONSTANTS_H