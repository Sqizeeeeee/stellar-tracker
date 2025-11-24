project(orbit_service LANGUAGES CXX)

add_executable(orbit_service
    src/main.cpp
    src/orbit_calculator.cpp
    proto/astro.pb.cc
    proto/astro.grpc.pb.cc
)

target_include_directories(orbit_service PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    proto
)

target_link_libraries(orbit_service
    protobuf
    grpc++
    grpc
    gpr
    pthread
)