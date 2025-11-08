#include "vector_ops.h"
#include <stdexcept>

namespace vector_ops {

double dotProduct(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != b.size()) {
        return 0.0;
    }
    
    double result = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        result += a[i] * b[i];
    }
    return result;
}

std::vector<double> crossProduct(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != 3 || b.size() != 3) {
        return {};
    }
    
    return {
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    };
}

double norm(const std::vector<double>& v) {
    double sum = 0.0;
    for (double value : v) {
        sum += value * value;
    }
    return std::sqrt(sum);
}

void normalize(std::vector<double>& v) {
    double length = norm(v);
    if (length > 0.0) {
        scale(v, 1.0 / length);
    }
}

void scale(std::vector<double>& v, double scalar) {
    for (double& value : v) {
        value *= scalar;
    }
}

std::vector<double> add(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != b.size()) {
        return {};
    }
    
    std::vector<double> result(a.size());
    for (size_t i = 0; i < a.size(); ++i) {
        result[i] = a[i] + b[i];
    }
    return result;
}

std::vector<double> subtract(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != b.size()) {
        return {};
    }
    
    std::vector<double> result(a.size());
    for (size_t i = 0; i < a.size(); ++i) {
        result[i] = a[i] - b[i];
    }
    return result;
}

} // namespace vector_ops