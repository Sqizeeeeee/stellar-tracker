cmake_minimum_required(VERSION 3.15)
project(orchestrator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

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
    proto
)

# Link libraries
target_link_libraries(orchestrator
    gRPC::grpc++
    protobuf::libprotobuf
    grpc++
    grpc
    gpr
    pthread
)

# Enable testing
enable_testing()
add_test(NAME basic_test COMMAND orchestrator --test)