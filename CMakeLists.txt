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

# Находим все исходные файлы
file(GLOB_RECURSE SRC_FILES 
    "src/*.cpp" 
    "src/*/*.cpp"
    "src/*/*/*.cpp"
)

# Основная библиотека
add_library(stellar_core STATIC ${SRC_FILES})

# Основная программа (пока заглушка)
add_executable(stellar_tracker_main src/main.cpp)
target_link_libraries(stellar_tracker_main stellar_core)

# Тесты
enable_testing()

# Тест 1: Базовая функциональность
add_executable(test_basic tests/test_basic.cpp)
target_link_libraries(test_basic stellar_core)
add_test(NAME test_basic COMMAND test_basic)

# Тест 2: Математические утилиты
add_executable(test_math_utils tests/test_math_utils.cpp)
target_link_libraries(test_math_utils stellar_core)
add_test(NAME test_math_utils COMMAND test_math_utils)

# Тест 3: Алгоритм Гаусса
add_executable(test_gauss tests/test_gauss.cpp)
target_link_libraries(test_gauss stellar_core)
add_test(NAME test_gauss COMMAND test_gauss)

# Группируем тесты
set(TEST_EXECUTABLES test_basic test_math_utils test_gauss)

# Выведем список файлов для отладки
message(STATUS "Found source files:")
foreach(file ${SRC_FILES})
    message(STATUS "  ${file}")
endforeach()

# Цели для удобства
add_custom_target(run_tests
    COMMAND ctest --output-on-failure
    DEPENDS ${TEST_EXECUTABLES}
    COMMENT "Running all tests..."
)

add_custom_target(build_all
    DEPENDS stellar_tracker_main ${TEST_EXECUTABLES}
    COMMENT "Building all targets..."
)