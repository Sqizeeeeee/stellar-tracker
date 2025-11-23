project(orchestrator LANGUAGES CXX)

add_executable(orchestrator
    src/main.cpp
    src/orchestrator_service.cpp
    proto/astro.pb.cc
    proto/astro.grpc.pb.cc
)

target_include_directories(orchestrator PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    proto
)

target_link_libraries(orchestrator
    protobuf
    grpc++
    grpc
    gpr
    pthread
)