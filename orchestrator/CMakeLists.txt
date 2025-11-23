cmake_minimum_required(VERSION 3.16)
project(orchestrator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# Просто указываем библиотеки напрямую — они точно есть в Ubuntu
add_executable(orchestrator
    src/main.cpp
    src/proto/astro.pb.cc
    src/proto/astro.grpc.pb.cc
)

target_include_directories(orchestrator PRIVATE
    /usr/include
    src/proto
)

target_link_libraries(orchestrator
    protobuf
    grpc++
    grpc
    pthread
)

target_compile_options(orchestrator PRIVATE -pthread)