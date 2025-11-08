#include <iostream>
#include <cmath>
#include "../src/math_utils/vector_ops.h"
#include "../src/math_utils/constants.h"

using namespace vector_ops;

bool test_dot_product() {
    std::vector<double> a = {1, 2, 3};
    std::vector<double> b = {4, 5, 6};
    double result = dotProduct(a, b);
    double expected = 32; // 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    return std::abs(result - expected) < 1e-10;
}

bool test_cross_product() {
    std::vector<double> a = {1, 0, 0};
    std::vector<double> b = {0, 1, 0};
    std::vector<double> result = crossProduct(a, b);
    std::vector<double> expected = {0, 0, 1};
    
    if (result.size() != expected.size()) return false;
    for (size_t i = 0; i < result.size(); ++i) {
        if (std::abs(result[i] - expected[i]) > 1e-10) return false;
    }
    return true;
}

bool test_norm() {
    std::vector<double> v = {3, 4, 0};
    double result = norm(v);
    double expected = 5.0; // sqrt(3^2 + 4^2) = 5
    return std::abs(result - expected) < 1e-10;
}

int main() {
    std::cout << "=== Тест математических утилит ===" << std::endl;
    
    int passed = 0;
    int total = 0;
    
    auto run_test = [&](const std::string& name, bool (*test)()) {
        total++;
        if (test()) {
            std::cout << "✅ " << name << " - PASSED" << std::endl;
            passed++;
        } else {
            std::cout << "❌ " << name << " - FAILED" << std::endl;
        }
    };
    
    run_test("Скалярное произведение", test_dot_product);
    run_test("Векторное произведение", test_cross_product);
    run_test("Норма вектора", test_norm);
    
    std::cout << "Результат: " << passed << "/" << total << " тестов пройдено" << std::endl;
    return (passed == total) ? 0 : 1;
}