#ifndef VECTOR_OPS_H
#define VECTOR_OPS_H

#include <vector>
#include <cmath>
#include "constants.h"

/**
 * @brief Пространство имён для операций с векторами
 */
namespace vector_ops {

/**
 * @brief Вычисляет скалярное произведение двух векторов
 * @param a Первый вектор
 * @param b Второй вектор
 * @return Скалярное произведение
 * @brief Если векторы разной длины, возвращает 0.0
 */
double dotProduct(const std::vector<double>& a, const std::vector<double>& b);

/**
 * @brief Вычисляет векторное произведение двух 3D векторов
 * @param a Первый вектор (должен быть размером 3)
 * @param b Второй вектор (должен быть размером 3)
 * @return Векторное произведение как вектор размером 3
 * @brief Если векторы не 3D, возвращает пустой вектор
 */
std::vector<double> crossProduct(const std::vector<double>& a, const std::vector<double>& b);

/**
 * @brief Вычисляет евклидову норму (длину) вектора
 * @param v Входной вектор
 * @return Длина вектора
 */
double norm(const std::vector<double>& v);

/**
 * @brief Нормализует вектор (делает его длину равной 1)
 * @param v Входной вектор (изменяется на месте)
 * @brief Если вектор нулевой, оставляет его без изменений
 */
void normalize(std::vector<double>& v);

/**
 * @brief Умножает вектор на скаляр
 * @param v Вектор (изменяется на месте)
 * @param scalar Скаляр для умножения
 */
void scale(std::vector<double>& v, double scalar);

/**
 * @brief Складывает два вектора
 * @param a Первый вектор
 * @param b Второй вектор
 * @return Результат сложения
 * @brief Если векторы разной длины, возвращает пустой вектор
 */
std::vector<double> add(const std::vector<double>& a, const std::vector<double>& b);

/**
 * @brief Вычитает два вектора
 * @param a Первый вектор
 * @param b Второй вектор  
 * @return Результат вычитания a - b
 * @brief Если векторы разной длины, возвращает пустой вектор
 */
std::vector<double> subtract(const std::vector<double>& a, const std::vector<double>& b);

} // namespace vector_ops

#endif // VECTOR_OPS_H