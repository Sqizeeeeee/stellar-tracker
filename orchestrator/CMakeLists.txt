cmake_minimum_required(VERSION 3.15)
project(orchestrator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Используем pkg-config для поиска библиотек
find_package(PkgConfig REQUIRED)
pkg_check_modules(PROTOBUF REQUIRED protobuf)
pkg_check_modules(GRPC REQUIRED grpc++)
pkg_check_modules(GRPCPP REQUIRED grpc++_unsecure)

# Add executable
add_executable(orchestrator
    src/main.cpp
    src/orchestrator_service.cpp
    src/metrics_server.cpp
    proto/astro.pb.cc
    proto/astro.grpc.pb.cc
)

target_include_directories(orchestrator PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/proto
    ${PROTOBUF_INCLUDE_DIRS}
    ${GRPC_INCLUDE_DIRS}
    ${GRPCPP_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(orchestrator
    ${PROTOBUF_LIBRARIES}
    ${GRPC_LIBRARIES}
    ${GRPCPP_LIBRARIES}
    pthread
)

# Enable testing
enable_testing()
add_test(NAME basic_test COMMAND orchestrator --test)