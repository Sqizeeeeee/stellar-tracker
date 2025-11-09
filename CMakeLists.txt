cmake_minimum_required(VERSION 3.15)
project(StellarTracker VERSION 1.0.0 LANGUAGES CXX)

# Настройки компилятора
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Опции компиляции
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g -O0")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")
endif()

# Включаем директории с исходным кодом
include_directories(${CMAKE_SOURCE_DIR}/src)

# ЯВНО перечисляем все исходные файлы
set(ALGORITHM_FILES
    src/algorithms/least_squares_determinator.cpp
    src/algorithms/orbital_elements_calculator.cpp
    src/algorithms/initial_orbit_estimator.cpp
    src/algorithms/fast_orbit_estimator.cpp
)

set(MATH_UTILS_FILES
    src/math_utils/earth_position.cpp
    src/math_utils/svd_solver.cpp
    src/math_utils/vector_ops.cpp
)

set(UTILS_FILES
    src/utils/csv_loader.cpp
)

set(MODELS_FILES
    # models - только .h файлы
)

# Объединяем все файлы
set(ALL_SRC_FILES
    ${ALGORITHM_FILES}
    ${MATH_UTILS_FILES}
    ${UTILS_FILES}
    src/main.cpp
)

# Основная библиотека
add_library(stellar_core STATIC ${ALL_SRC_FILES})

# Основная программа
add_executable(stellar_tracker_main src/main.cpp)
target_link_libraries(stellar_tracker_main stellar_core)

# Тесты
enable_testing()

# Тест кометы Энке
add_executable(test_encke tests/test_encke.cpp)
target_link_libraries(test_encke stellar_core)
add_test(NAME test_encke COMMAND test_encke)

# Тест кометы Галлея
add_executable(test_halley tests/test_halley.cpp)
target_link_libraries(test_halley stellar_core)
add_test(NAME test_halley COMMAND test_halley)

# Бенчмарк производительности
add_executable(benchmark tests/benchmark.cpp)
target_link_libraries(benchmark stellar_core)

# Цели для удобства
add_custom_target(run_tests
    COMMAND ctest --output-on-failure
    DEPENDS test_encke test_halley
    COMMENT "Running comet tests..."
)

add_custom_target(build_all
    DEPENDS stellar_tracker_main test_encke test_halley benchmark
    COMMENT "Building all targets..."
)