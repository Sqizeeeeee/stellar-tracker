cmake_minimum_required(VERSION 3.16)
project(stellar_tracker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# Флаг для включения/выключения сборки orbit-service
option(BUILD_ORBIT_SERVICE "Build orbit service" ON)

# Добавляем поддиректории
add_subdirectory(orchestrator)

if(BUILD_ORBIT_SERVICE)
    add_subdirectory(orbit-service)
endif()