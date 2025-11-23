cmake_minimum_required(VERSION 3.16)
project(stellar_tracker LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# Добавляем поддиректории
add_subdirectory(orchestrator)
add_subdirectory(orbit-service)