cmake_minimum_required(VERSION 3.22)
project(DFTTEST2_GCC_Package)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
find_package(Threads REQUIRED)

# Define the include path relative to this wrapper
set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

# Fix version detection
if(SKBUILD_PROJECT_VERSION AND NOT VCS_TAG)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(GIT_FOUND OFF CACHE BOOL "Disable git in submodule to avoid error messages")
endif()

set(ENABLE_CUDA OFF CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC ON CACHE BOOL "" FORCE)
set(ENABLE_HIP OFF CACHE BOOL "" FORCE)

# Add the submodule but skip its internal install rules
add_subdirectory(vs-dfttest2 EXCLUDE_FROM_ALL)
target_link_libraries(dfttest2_gcc PRIVATE Threads::Threads)

add_custom_target(build_gcc ALL DEPENDS dfttest2_gcc)
install(TARGETS dfttest2_gcc LIBRARY DESTINATION .)
