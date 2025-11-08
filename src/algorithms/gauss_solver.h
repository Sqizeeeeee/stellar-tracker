#ifndef GAUSS_SOLVER_H
#define GAUSS_SOLVER_H

#include <vector>
#include "../models/observation.h"
#include "../models/orbital_elements.h"

/**
 * @brief Класс для определения орбиты кометы методом Гаусса
 * 
 * Реализует классический метод Гаусса с возможностью обработки
 * трёх и более наблюдений. Для >3 наблюдений используется
 * метод наименьших квадратов.
 */
class GaussSolver {
public:
    /**
     * @brief Конструктор с минимальным количеством наблюдений
     * @param min_observations Минимальное число наблюдений (по умолчанию 3)
     */
    explicit GaussSolver(int min_observations = 3);
    
    /**
     * @brief Определяет орбитальные элементы по наблюдениям
     * @param observations Вектор наблюдений (минимум 3)
     * @return Орбитальные элементы кометы
     * @brief Выбрасывает исключение при недостаточном количестве наблюдений
     */
    OrbitalElements determineOrbit(const std::vector<Observation>& observations);
    
    /**
     * @brief Устанавливает точность для итерационных методов
     * @param tolerance Точность вычислений
     */
    void setTolerance(double tolerance);
    
    /**
     * @brief Возвращает количество использованных наблюдений в последнем расчёте
     * @return Количество наблюдений
     */
    int getUsedObservationsCount() const;

private:
    int min_observations_;
    double tolerance_;
    int last_used_observations_;
    
    /**
     * @brief Проверяет валидность входных наблюдений
     * @param observations Вектор наблюдений для проверки
     * @brief Выбрасывает исключение при невалидных данных
     */
    void validateObservations(const std::vector<Observation>& observations);
    
    /**
     * @brief Классический метод Гаусса для 3 наблюдений
     * @param observations Ровно 3 наблюдения
     * @return Орбитальные элементы
     */
    OrbitalElements solveThreeObservations(const std::vector<Observation>& observations);
    
    /**
     * @brief Метод Гаусса с наименьшими квадратами для 4+ наблюдений
     * @param observations 4 или более наблюдений
     * @return Уточнённые орбитальные элементы
     */
    OrbitalElements solveMultipleObservations(const std::vector<Observation>& observations);
    
    /**
     * @brief Вычисляет геоцентрические координаты Земли на заданную юлианскую дату
     * @param jd Юлианская дата
     * @return Вектор [x, y, z] координат Земли в а.е.
     */
    std::vector<double> calculateEarthPosition(double jd);
    
    /**
     * @brief Решает систему уравнений для метода Гаусса
     * @param coefficients Матрица коэффициентов
     * @param constants Вектор правых частей
     * @return Вектор решений
     */
    std::vector<double> solveLinearSystem(const std::vector<std::vector<double>>& coefficients, 
                                         const std::vector<double>& constants);
    
    /**
     * @brief Преобразует сферические координаты в декартовы
     * @param ra Прямое восхождение в радианах
     * @param dec Склонение в радианах
     * @return Единичный вектор направления [x, y, z]
     */
    std::vector<double> sphericalToCartesian(double ra, double dec);
};

#endif // GAUSS_SOLVER_H