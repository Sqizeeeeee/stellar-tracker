#include "svd_solver.h"
#include <cmath>
#include <stdexcept>
#include <iostream>
#include <algorithm>

/**
 * @brief Решение системы линейных уравнений методом наименьших квадратов через SVD
 * @param A Матрица коэффициентов размера M x N
 * @param b Вектор правой части размера M
 * @return Вектор решения размера N
 */
std::vector<double> SVDSolver::solveLeastSquares(
    const std::vector<std::vector<double>>& A,
    const std::vector<double>& b) {
    
    //brief: Проверка входных данных
    if (A.empty() || b.empty()) {
        throw std::invalid_argument("Пустая матрица или вектор");
    }
    
    size_t M = A.size();    // Число уравнений
    size_t N = A[0].size(); // Число переменных
    
    if (M < N) {
        throw std::invalid_argument("Недоопределённая система: уравнений меньше чем переменных");
    }
    
    if (b.size() != M) {
        throw std::invalid_argument("Несовместимые размеры матрицы и вектора");
    }
    
    //brief: Выполняем SVD разложение
    std::vector<std::vector<double>> U(M, std::vector<double>(M, 0.0));
    std::vector<double> S(N, 0.0);
    std::vector<std::vector<double>> V(N, std::vector<double>(N, 0.0));
    
    decomposeSVD(A, U, S, V);
    
    //brief: Проверяем обусловленность системы
    double cond = conditionNumber(A);
    std::cout << "Число обусловленности: " << cond << std::endl;
    if (cond > 1e10) {
        std::cout << "⚠️  Предупреждение: плохо обусловленная система" << std::endl;
    }
    
    //brief: Решение: x = V * Σ⁺ * Uᵀ * b
    std::vector<double> x(N, 0.0);
    
    //brief: Вычисляем Uᵀ * b
    std::vector<double> Ut_b(N, 0.0);
    for (size_t i = 0; i < N; ++i) {
        for (size_t j = 0; j < M; ++j) {
            Ut_b[i] += U[j][i] * b[j]; // Uᵀ[i,j] = U[j,i]
        }
    }
    
    //brief: Умножаем на псевдообратную диагональ Σ⁺
    std::vector<double> S_inv_Ut_b(N, 0.0);
    for (size_t i = 0; i < N; ++i) {
        if (std::abs(S[i]) > 1e-12) { // Отбрасываем малые сингулярные значения
            S_inv_Ut_b[i] = Ut_b[i] / S[i];
        }
    }
    
    //brief: Умножаем на V
    for (size_t i = 0; i < N; ++i) {
        for (size_t j = 0; j < N; ++j) {
            x[i] += V[i][j] * S_inv_Ut_b[j];
        }
    }
    
    return x;
}

/**
 * @brief Сингулярное разложение матрицы (упрощённый алгоритм)
 * @param A Исходная матрица MxN
 * @param U Левые сингулярные векторы MxM
 * @param S Сингулярные значения (диагональ)
 * @param V Правые сингулярные векторы NxN
 */
void SVDSolver::decomposeSVD(const std::vector<std::vector<double>>& A,
                           std::vector<std::vector<double>>& U,
                           std::vector<double>& S,
                           std::vector<std::vector<double>>& V) {
    
    size_t M = A.size();
    size_t N = A[0].size();
    
    //brief: Инициализация матриц
    U = std::vector<std::vector<double>>(M, std::vector<double>(M, 0.0));
    V = std::vector<std::vector<double>>(N, std::vector<double>(N, 0.0));
    S = std::vector<double>(N, 0.0);
    
    //brief: Вычисляем A^T * A для нахождения правых сингулярных векторов
    std::vector<std::vector<double>> AtA(N, std::vector<double>(N, 0.0));
    for (size_t i = 0; i < N; ++i) {
        for (size_t j = 0; j < N; ++j) {
            for (size_t k = 0; k < M; ++k) {
                AtA[i][j] += A[k][i] * A[k][j];
            }
        }
    }
    
    //brief: Упрощённый метод - используем степенной метод для нахождения собственных значений
    //brief: В реальной реализации следует использовать алгоритм Якоби или QR-разложение
    const int max_iterations = 100;
    const double tolerance = 1e-12;
    
    for (size_t i = 0; i < N; ++i) {
        //brief: Начальное приближение для собственного вектора
        std::vector<double> v(N, 0.0);
        v[i] = 1.0;  // Начинаем с базисного вектора
        
        double sigma_old = 0.0;
        
        for (int iter = 0; iter < max_iterations; ++iter) {
            //brief: Умножаем AtA на v
            std::vector<double> Av(N, 0.0);
            for (size_t j = 0; j < N; ++j) {
                for (size_t k = 0; k < N; ++k) {
                    Av[j] += AtA[j][k] * v[k];
                }
            }
            
            //brief: Вычисляем норму и сингулярное значение
            double norm = 0.0;
            for (double val : Av) {
                norm += val * val;
            }
            norm = std::sqrt(norm);
            
            //brief: Нормализуем вектор
            for (size_t j = 0; j < N; ++j) {
                v[j] = Av[j] / norm;
            }
            
            //brief: Вычисляем сингулярное значение
            double sigma = 0.0;
            for (size_t j = 0; j < N; ++j) {
                for (size_t k = 0; k < N; ++k) {
                    sigma += v[j] * AtA[j][k] * v[k];
                }
            }
            sigma = std::sqrt(sigma);
            
            //brief: Проверка сходимости
            if (std::abs(sigma - sigma_old) < tolerance) {
                S[i] = sigma;
                //brief: Сохраняем правый сингулярный вектор
                for (size_t j = 0; j < N; ++j) {
                    V[j][i] = v[j];
                }
                break;
            }
            
            sigma_old = sigma;
        }
        
        //brief: Вычисляем левый сингулярный вектор u = A * v / sigma
        if (S[i] > 1e-12) {
            for (size_t j = 0; j < M; ++j) {
                for (size_t k = 0; k < N; ++k) {
                    U[j][i] += A[j][k] * V[k][i];
                }
                U[j][i] /= S[i];
            }
        }
    }
}

/**
 * @brief Проверка обусловленности матрицы
 * @param A Матрица для анализа
 * @return Число обусловленности (чем больше - тем хуже)
 */
double SVDSolver::conditionNumber(const std::vector<std::vector<double>>& A) {
    if (A.empty()) return 0.0;
    
    //brief: Для упрощения используем отношение максимального и минимального сингулярного значения
    std::vector<std::vector<double>> U, V;
    std::vector<double> S;
    
    decomposeSVD(A, U, S, V);
    
    double sigma_max = 0.0;
    double sigma_min = std::numeric_limits<double>::max();
    
    for (double sigma : S) {
        if (sigma > sigma_max) sigma_max = sigma;
        if (sigma > 1e-12 && sigma < sigma_min) sigma_min = sigma;
    }
    
    if (sigma_min == std::numeric_limits<double>::max()) {
        return std::numeric_limits<double>::infinity();
    }
    
    return sigma_max / sigma_min;
}

/**
 * @brief Умножение матрицы на вектор
 * @param A Матрица MxN
 * @param x Вектор размера N
 * @return Вектор результата размера M
 */
std::vector<double> SVDSolver::matrixVectorMultiply(
    const std::vector<std::vector<double>>& A,
    const std::vector<double>& x) {
    
    if (A.empty() || x.size() != A[0].size()) {
        throw std::invalid_argument("Несовместимые размеры матрицы и вектора");
    }
    
    std::vector<double> result(A.size(), 0.0);
    for (size_t i = 0; i < A.size(); ++i) {
        for (size_t j = 0; j < A[i].size(); ++j) {
            result[i] += A[i][j] * x[j];
        }
    }
    return result;
}

/**
 * @brief Транспонирование матрицы
 * @param A Исходная матрица MxN
 * @return Транспонированная матрица NxM
 */
std::vector<std::vector<double>> SVDSolver::transpose(
    const std::vector<std::vector<double>>& A) {
    
    if (A.empty()) return {};
    
    size_t M = A.size();
    size_t N = A[0].size();
    
    std::vector<std::vector<double>> result(N, std::vector<double>(M, 0.0));
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = 0; j < N; ++j) {
            result[j][i] = A[i][j];
        }
    }
    return result;
}