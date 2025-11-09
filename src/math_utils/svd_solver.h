#ifndef SVD_SOLVER_H
#define SVD_SOLVER_H

#include <vector>

/**
 * @brief Класс для решения систем линейных уравнений методом SVD
 * 
 * Реализует сингулярное разложение матриц (SVD) для решения 
 * переопределённых и плохо обусловленных систем уравнений.
 * Обеспечивает численную устойчивость и минимальную норму решения.
 */
class SVDSolver {
public:
    /**
     * @brief Решение системы линейных уравнений методом наименьших квадратов
     * @param A Матрица коэффициентов размера M x N
     * @param b Вектор правой части размера M
     * @return Вектор решения размера N
     * @throws std::invalid_argument При несовместимых размерах
     */
    static std::vector<double> solveLeastSquares(
        const std::vector<std::vector<double>>& A,
        const std::vector<double>& b);
    
    /**
     * @brief Проверка обусловленности матрицы
     * @param A Матрица для анализа
     * @return Число обусловленности (чем больше - тем хуже)
     */
    static double conditionNumber(const std::vector<std::vector<double>>& A);

private:
    /**
     * @brief Сингулярное разложение матрицы (алгоритм Голуба-Рейнша)
     * @param A Исходная матрица MxN
     * @param U Левые сингулярные векторы MxM
     * @param S Сингулярные значения (диагональ)
     * @param V Правые сингулярные векторы NxN
     */
    static void decomposeSVD(const std::vector<std::vector<double>>& A,
                           std::vector<std::vector<double>>& U,
                           std::vector<double>& S,
                           std::vector<std::vector<double>>& V);
    
    /**
     * @brief Умножение матрицы на вектор
     * @param A Матрица MxN
     * @param x Вектор размера N
     * @return Вектор результата размера M
     */
    static std::vector<double> matrixVectorMultiply(
        const std::vector<std::vector<double>>& A,
        const std::vector<double>& x);
    
    /**
     * @brief Транспонирование матрицы
     * @param A Исходная матрица MxN
     * @return Транспонированная матрица NxM
     */
    static std::vector<std::vector<double>> transpose(
        const std::vector<std::vector<double>>& A);
};

#endif