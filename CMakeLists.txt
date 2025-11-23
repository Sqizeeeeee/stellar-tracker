cmake_minimum_required(VERSION 3.20)
project(astro-orbit-service LANGUAGES CXX)

# Подключаем vcpkg автоматически
set(CMAKE_TOOLCHAIN_FILE 
    "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
    CACHE STRING "Vcpkg toolchain file")

# Стандарт C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Добавляем все C++ сервисы
add_subdirectory(orchestrator)
# add_subdirectory(orbit-service)  # когда будет готов