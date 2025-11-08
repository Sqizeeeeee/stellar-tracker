#ifndef ORBITAL_ELEMENTS_CALCULATOR_H
#define ORBITAL_ELEMENTS_CALCULATOR_H

#include <vector>
#include "../models/orbital_elements.h"

/**
 * @brief Класс для вычисления орбитальных элементов из векторов положения и скорости
 */
class OrbitalElementsCalculator {
public:
    /**
     * @brief Вычисляет орбитальные элементы из положения и скорости
     * @param position Вектор положения [x, y, z] в а.е.
     * @param velocity Вектор скорости [vx, vy, vz] в а.е./сутки
     * @param jd Юлианская дата для которой вычислены векторы
     * @return Орбитальные элементы
     */
    static OrbitalElements calculateFromVectors(const std::vector<double>& position, 
                                               const std::vector<double>& velocity, 
                                               double jd);
    
    /**
     * @brief Вычисляет векторы положения и скорости из трёх позиций (метод Гиббса)
     * @param r1 Первая позиция [x, y, z]
     * @param r2 Вторая позиция [x, y, z] 
     * @param r3 Третья позиция [x, y, z]
     * @param t1 Время первой позиции (JD)
     * @param t2 Время второй позиции (JD)
     * @param t3 Время третьей позиции (JD)
     * @return Пара: вектор положения и вектор скорости для времени t2
     */
    static std::pair<std::vector<double>, std::vector<double>> 
    gibbsMethod(const std::vector<double>& r1, const std::vector<double>& r2, const std::vector<double>& r3,
                double t1, double t2, double t3);

private:
    /**
     * @brief Вычисляет вектор удельного момента
     */
    static std::vector<double> calculateAngularMomentum(const std::vector<double>& position, 
                                                       const std::vector<double>& velocity);
    
    /**
     * @brief Вычисляет вектор Лапласа-Рунге-Ленца
     */
    static std::vector<double> calculateLaplaceVector(const std::vector<double>& position, 
                                                     const std::vector<double>& velocity, 
                                                     const std::vector<double>& angular_momentum);
};

#endif // ORBITAL_ELEMENTS_CALCULATOR_H