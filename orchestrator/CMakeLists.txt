project(orchestrator LANGUAGES CXX)

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

target_link_libraries(orchestrator
    protobuf
    grpc++
    grpc
    gpr
    pthread
)